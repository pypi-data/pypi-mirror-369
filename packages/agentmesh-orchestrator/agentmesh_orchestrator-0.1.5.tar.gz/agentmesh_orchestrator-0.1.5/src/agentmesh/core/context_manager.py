"""Context management system for agent conversations and state."""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import uuid4

import redis.asyncio as redis
from pydantic import BaseModel

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class ContextScope(str):
    """Context scope constants."""
    AGENT = "agent"
    CONVERSATION = "conversation"
    GROUP = "group"
    GLOBAL = "global"


class AccessLevel(str):
    """Access level constants."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class ContextEntry(BaseModel):
    """Individual context entry."""
    id: str
    key: str
    value: Any
    scope: str
    scope_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    metadata: Dict[str, Any] = {}
    expires_at: Optional[datetime] = None


class ContextVersion(BaseModel):
    """Context version for history tracking."""
    version: int
    value: Any
    updated_by: str
    updated_at: datetime
    change_reason: Optional[str] = None


class ContextAccessControl(BaseModel):
    """Access control for context entries."""
    entry_id: str
    agent_id: str
    access_level: str
    granted_by: str
    granted_at: datetime


class ContextManager:
    """Manages context storage, versioning, and access control for agents."""
    
    def __init__(self):
        """Initialize the context manager."""
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                db=self.settings.redis_db + 1,  # Use different DB for context
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis context store")
        except Exception as e:
            logger.error(f"Failed to connect to Redis for context: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis context store")
    
    async def set_context(
        self,
        key: str,
        value: Any,
        scope: str,
        scope_id: str,
        created_by: str,
        metadata: Optional[Dict[str, Any]] = None,
        expires_in: Optional[timedelta] = None,
        change_reason: Optional[str] = None
    ) -> ContextEntry:
        """Set a context entry with versioning."""
        if not self.redis_client:
            await self.connect()
        
        entry_id = f"{scope}:{scope_id}:{key}"
        now = datetime.utcnow()
        expires_at = now + expires_in if expires_in else None
        
        # Get existing entry for versioning
        existing_entry = await self.get_context(key, scope, scope_id, created_by)
        version = (existing_entry.version + 1) if existing_entry else 1
        
        # Create new context entry
        entry = ContextEntry(
            id=entry_id,
            key=key,
            value=value,
            scope=scope,
            scope_id=scope_id,
            created_by=created_by,
            created_at=existing_entry.created_at if existing_entry else now,
            updated_at=now,
            version=version,
            metadata=metadata or {},
            expires_at=expires_at
        )
        
        try:
            # Store the entry
            entry_data = entry.model_dump_json()
            await self.redis_client.hset("context_entries", entry_id, entry_data)
            
            # Store version history
            if existing_entry:
                version_entry = ContextVersion(
                    version=version,
                    value=value,
                    updated_by=created_by,
                    updated_at=now,
                    change_reason=change_reason
                )
                await self.redis_client.lpush(
                    f"context_history:{entry_id}",
                    version_entry.model_dump_json()
                )
                # Keep only last 100 versions
                await self.redis_client.ltrim(f"context_history:{entry_id}", 0, 99)
            
            # Set expiration if specified
            if expires_at:
                expire_seconds = int((expires_at - now).total_seconds())
                await self.redis_client.expire(f"context_entries:{entry_id}", expire_seconds)
            
            # Index by scope for querying
            await self.redis_client.sadd(f"context_scope:{scope}:{scope_id}", entry_id)
            
            logger.debug(f"Context set: {entry_id} v{version}")
            return entry
            
        except Exception as e:
            logger.error(f"Failed to set context {entry_id}: {e}")
            raise
    
    async def get_context(
        self,
        key: str,
        scope: str,
        scope_id: str,
        requester_id: str,
        version: Optional[int] = None
    ) -> Optional[ContextEntry]:
        """Get a context entry with access control."""
        if not self.redis_client:
            await self.connect()
        
        entry_id = f"{scope}:{scope_id}:{key}"
        
        try:
            # Check access permissions
            if not await self._check_access(entry_id, requester_id, AccessLevel.READ):
                logger.warning(f"Access denied for {requester_id} to read {entry_id}")
                return None
            
            # Get current entry
            if version is None:
                entry_data = await self.redis_client.hget("context_entries", entry_id)
                if entry_data:
                    return ContextEntry(**json.loads(entry_data))
            else:
                # Get specific version from history
                history = await self.redis_client.lrange(f"context_history:{entry_id}", 0, -1)
                for version_data in history:
                    version_entry = ContextVersion(**json.loads(version_data))
                    if version_entry.version == version:
                        # Reconstruct entry with historical value
                        current_entry_data = await self.redis_client.hget("context_entries", entry_id)
                        if current_entry_data:
                            current_entry = ContextEntry(**json.loads(current_entry_data))
                            current_entry.value = version_entry.value
                            current_entry.version = version
                            current_entry.updated_at = version_entry.updated_at
                            return current_entry
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get context {entry_id}: {e}")
            return None
    
    async def delete_context(
        self,
        key: str,
        scope: str,
        scope_id: str,
        requester_id: str
    ) -> bool:
        """Delete a context entry."""
        if not self.redis_client:
            await self.connect()
        
        entry_id = f"{scope}:{scope_id}:{key}"
        
        try:
            # Check access permissions
            if not await self._check_access(entry_id, requester_id, AccessLevel.WRITE):
                logger.warning(f"Access denied for {requester_id} to delete {entry_id}")
                return False
            
            # Delete entry and related data
            await self.redis_client.hdel("context_entries", entry_id)
            await self.redis_client.delete(f"context_history:{entry_id}")
            await self.redis_client.delete(f"context_access:{entry_id}")
            await self.redis_client.srem(f"context_scope:{scope}:{scope_id}", entry_id)
            
            logger.debug(f"Context deleted: {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete context {entry_id}: {e}")
            return False
    
    async def list_context(
        self,
        scope: str,
        scope_id: str,
        requester_id: str,
        key_pattern: Optional[str] = None
    ) -> List[ContextEntry]:
        """List context entries in a scope."""
        if not self.redis_client:
            await self.connect()
        
        try:
            # Get all entry IDs in scope
            entry_ids = await self.redis_client.smembers(f"context_scope:{scope}:{scope_id}")
            
            entries = []
            for entry_id in entry_ids:
                # Filter by key pattern if specified
                if key_pattern:
                    key = entry_id.split(":")[-1]
                    if key_pattern not in key:
                        continue
                
                # Check access permissions
                if await self._check_access(entry_id, requester_id, AccessLevel.READ):
                    entry_data = await self.redis_client.hget("context_entries", entry_id)
                    if entry_data:
                        entries.append(ContextEntry(**json.loads(entry_data)))
            
            return sorted(entries, key=lambda e: e.updated_at, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list context for {scope}:{scope_id}: {e}")
            return []
    
    async def get_context_history(
        self,
        key: str,
        scope: str,
        scope_id: str,
        requester_id: str,
        limit: int = 50
    ) -> List[ContextVersion]:
        """Get version history for a context entry."""
        if not self.redis_client:
            await self.connect()
        
        entry_id = f"{scope}:{scope_id}:{key}"
        
        try:
            # Check access permissions
            if not await self._check_access(entry_id, requester_id, AccessLevel.READ):
                logger.warning(f"Access denied for {requester_id} to read history {entry_id}")
                return []
            
            # Get version history
            history_data = await self.redis_client.lrange(f"context_history:{entry_id}", 0, limit-1)
            
            versions = []
            for version_data in history_data:
                versions.append(ContextVersion(**json.loads(version_data)))
            
            return versions
            
        except Exception as e:
            logger.error(f"Failed to get context history {entry_id}: {e}")
            return []
    
    async def grant_access(
        self,
        key: str,
        scope: str,
        scope_id: str,
        agent_id: str,
        access_level: str,
        granted_by: str
    ) -> bool:
        """Grant access to a context entry."""
        if not self.redis_client:
            await self.connect()
        
        entry_id = f"{scope}:{scope_id}:{key}"
        
        try:
            # Check if granter has admin access
            if not await self._check_access(entry_id, granted_by, AccessLevel.ADMIN):
                logger.warning(f"Access denied for {granted_by} to grant access to {entry_id}")
                return False
            
            access_control = ContextAccessControl(
                entry_id=entry_id,
                agent_id=agent_id,
                access_level=access_level,
                granted_by=granted_by,
                granted_at=datetime.utcnow()
            )
            
            await self.redis_client.hset(
                f"context_access:{entry_id}",
                agent_id,
                access_control.model_dump_json()
            )
            
            logger.debug(f"Access granted: {agent_id} -> {access_level} on {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to grant access: {e}")
            return False
    
    async def revoke_access(
        self,
        key: str,
        scope: str,
        scope_id: str,
        agent_id: str,
        revoked_by: str
    ) -> bool:
        """Revoke access to a context entry."""
        if not self.redis_client:
            await self.connect()
        
        entry_id = f"{scope}:{scope_id}:{key}"
        
        try:
            # Check if revoker has admin access
            if not await self._check_access(entry_id, revoked_by, AccessLevel.ADMIN):
                logger.warning(f"Access denied for {revoked_by} to revoke access to {entry_id}")
                return False
            
            await self.redis_client.hdel(f"context_access:{entry_id}", agent_id)
            
            logger.debug(f"Access revoked: {agent_id} from {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke access: {e}")
            return False
    
    async def _check_access(
        self,
        entry_id: str,
        agent_id: str,
        required_level: str
    ) -> bool:
        """Check if an agent has the required access level to an entry."""
        if not self.redis_client:
            return False
        
        try:
            # Parse entry ID to get creator info
            scope, scope_id, key = entry_id.split(":", 2)
            
            # Get entry to check creator
            entry_data = await self.redis_client.hget("context_entries", entry_id)
            if entry_data:
                entry = ContextEntry(**json.loads(entry_data))
                # Creator always has admin access
                if entry.created_by == agent_id:
                    return True
            
            # Check explicit access permissions
            access_data = await self.redis_client.hget(f"context_access:{entry_id}", agent_id)
            if access_data:
                access_control = ContextAccessControl(**json.loads(access_data))
                return self._access_level_sufficient(access_control.access_level, required_level)
            
            # Default access rules based on scope
            if scope == ContextScope.AGENT:
                # Agent can access their own context
                return scope_id == agent_id
            elif scope == ContextScope.CONVERSATION:
                # Check if agent is part of the conversation
                # This could be enhanced to check conversation participants
                return agent_id in scope_id.split(":")
            elif scope == ContextScope.GROUP:
                # Check if agent is member of the group
                # This would require integration with group membership
                return True  # Simplified for now
            elif scope == ContextScope.GLOBAL:
                # Global context readable by all, writable by admins only
                return required_level == AccessLevel.READ
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking access for {agent_id} to {entry_id}: {e}")
            return False
    
    def _access_level_sufficient(self, granted_level: str, required_level: str) -> bool:
        """Check if granted access level is sufficient for required level."""
        level_hierarchy = {
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2,
            AccessLevel.ADMIN: 3
        }
        
        granted_value = level_hierarchy.get(granted_level, 0)
        required_value = level_hierarchy.get(required_level, 0)
        
        return granted_value >= required_value


# Global context manager instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get or create the global context manager instance."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
