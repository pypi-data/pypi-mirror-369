"""Handoff management system for agent transitions and workflow orchestration."""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

import redis.asyncio as redis
from pydantic import BaseModel

from ..core.config import get_settings
from ..messaging.message_bus import get_message_bus, MessageType
from .context_manager import get_context_manager, ContextScope

logger = logging.getLogger(__name__)


class HandoffReason(str):
    """Handoff reason constants."""
    TASK_COMPLETION = "task_completion"
    EXPERTISE_REQUIRED = "expertise_required"
    WORKLOAD_DISTRIBUTION = "workload_distribution"
    ERROR_ESCALATION = "error_escalation"
    USER_REQUEST = "user_request"
    TIMEOUT = "timeout"
    MANUAL = "manual"


class HandoffStatus(str):
    """Handoff status constants."""
    INITIATED = "initiated"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class HandoffRequest(BaseModel):
    """Handoff request model."""
    id: str
    from_agent_id: str
    to_agent_id: str
    conversation_id: Optional[str] = None
    reason: str
    message: str
    context_data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    created_at: datetime
    expires_at: Optional[datetime] = None
    priority: int = 0  # Higher number = higher priority


class HandoffResponse(BaseModel):
    """Handoff response model."""
    handoff_id: str
    accepted: bool
    message: Optional[str] = None
    responded_by: str
    responded_at: datetime


class HandoffAuditEntry(BaseModel):
    """Audit entry for handoff events."""
    id: str
    handoff_id: str
    event_type: str  # 'created', 'accepted', 'rejected', 'completed', 'cancelled'
    agent_id: str
    timestamp: datetime
    details: Dict[str, Any] = {}


class HandoffSummary(BaseModel):
    """Summary of a completed handoff."""
    handoff_id: str
    from_agent_id: str
    to_agent_id: str
    reason: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    context_transferred: bool = False
    conversation_id: Optional[str] = None


class HandoffManager:
    """Manages agent handoffs and workflow transitions."""
    
    def __init__(self):
        """Initialize the handoff manager."""
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        self.message_bus = get_message_bus()
        self.context_manager = get_context_manager()
        
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                db=self.settings.redis_db + 2,  # Use different DB for handoffs
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis handoff store")
        except Exception as e:
            logger.error(f"Failed to connect to Redis for handoffs: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis handoff store")
    
    async def initiate_handoff(
        self,
        from_agent_id: str,
        to_agent_id: str,
        reason: str,
        message: str,
        conversation_id: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        expires_in_minutes: int = 60
    ) -> HandoffRequest:
        """Initiate a handoff request."""
        if not self.redis_client:
            await self.connect()
        
        handoff_id = str(uuid4())
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=expires_in_minutes) if expires_in_minutes > 0 else None
        
        handoff_request = HandoffRequest(
            id=handoff_id,
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            conversation_id=conversation_id,
            reason=reason,
            message=message,
            context_data=context_data or {},
            metadata=metadata or {},
            created_at=now,
            expires_at=expires_at,
            priority=priority
        )
        
        try:
            # Store handoff request
            await self.redis_client.hset(
                "handoff_requests",
                handoff_id,
                handoff_request.model_dump_json()
            )
            
            # Add to pending handoffs for the target agent
            await self.redis_client.zadd(
                f"pending_handoffs:{to_agent_id}",
                {handoff_id: priority}
            )
            
            # Set expiration if specified
            if expires_at:
                expire_seconds = int((expires_at - now).total_seconds())
                await self.redis_client.expire(f"handoff_requests:{handoff_id}", expire_seconds)
            
            # Create audit entry
            await self._create_audit_entry(
                handoff_id=handoff_id,
                event_type="created",
                agent_id=from_agent_id,
                details={
                    "to_agent_id": to_agent_id,
                    "reason": reason,
                    "priority": priority
                }
            )
            
            # Send notification message to target agent
            await self.message_bus.send_message(
                sender_id=from_agent_id,
                receiver_id=to_agent_id,
                content=f"Handoff request: {message}",
                message_type=MessageType.HANDOFF,
                metadata={
                    "handoff_id": handoff_id,
                    "reason": reason,
                    "priority": priority,
                    "expires_at": expires_at.isoformat() if expires_at else None
                }
            )
            
            logger.info(f"Handoff initiated: {handoff_id} from {from_agent_id} to {to_agent_id}")
            return handoff_request
            
        except Exception as e:
            logger.error(f"Failed to initiate handoff: {e}")
            raise
    
    async def respond_to_handoff(
        self,
        handoff_id: str,
        agent_id: str,
        accepted: bool,
        message: Optional[str] = None
    ) -> HandoffResponse:
        """Respond to a handoff request."""
        if not self.redis_client:
            await self.connect()
        
        try:
            # Get handoff request
            handoff_data = await self.redis_client.hget("handoff_requests", handoff_id)
            if not handoff_data:
                raise ValueError(f"Handoff request {handoff_id} not found")
            
            handoff_request = HandoffRequest(**json.loads(handoff_data))
            
            # Verify agent is the target
            if handoff_request.to_agent_id != agent_id:
                raise ValueError(f"Agent {agent_id} is not the target of handoff {handoff_id}")
            
            # Check if already responded
            response_data = await self.redis_client.hget("handoff_responses", handoff_id)
            if response_data:
                raise ValueError(f"Handoff {handoff_id} has already been responded to")
            
            now = datetime.utcnow()
            
            # Create response
            response = HandoffResponse(
                handoff_id=handoff_id,
                accepted=accepted,
                message=message,
                responded_by=agent_id,
                responded_at=now
            )
            
            # Store response
            await self.redis_client.hset(
                "handoff_responses",
                handoff_id,
                response.model_dump_json()
            )
            
            # Remove from pending handoffs
            await self.redis_client.zrem(f"pending_handoffs:{agent_id}", handoff_id)
            
            # Update handoff status
            status = HandoffStatus.ACCEPTED if accepted else HandoffStatus.REJECTED
            await self.redis_client.hset(
                "handoff_status",
                handoff_id,
                json.dumps({
                    "status": status,
                    "updated_at": now.isoformat(),
                    "updated_by": agent_id
                })
            )
            
            # Create audit entry
            await self._create_audit_entry(
                handoff_id=handoff_id,
                event_type="accepted" if accepted else "rejected",
                agent_id=agent_id,
                details={"message": message} if message else {}
            )
            
            # If accepted, transfer context and complete handoff
            if accepted:
                await self._transfer_context(handoff_request)
                await self._complete_handoff(handoff_id, handoff_request)
            
            # Send response message to initiating agent
            await self.message_bus.send_message(
                sender_id=agent_id,
                receiver_id=handoff_request.from_agent_id,
                content=f"Handoff {'accepted' if accepted else 'rejected'}: {message or 'No message'}",
                message_type=MessageType.HANDOFF,
                metadata={
                    "handoff_id": handoff_id,
                    "accepted": accepted,
                    "response_type": "handoff_response"
                }
            )
            
            logger.info(f"Handoff {handoff_id} {'accepted' if accepted else 'rejected'} by {agent_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to respond to handoff {handoff_id}: {e}")
            raise
    
    async def cancel_handoff(
        self,
        handoff_id: str,
        agent_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel a handoff request."""
        if not self.redis_client:
            await self.connect()
        
        try:
            # Get handoff request
            handoff_data = await self.redis_client.hget("handoff_requests", handoff_id)
            if not handoff_data:
                return False
            
            handoff_request = HandoffRequest(**json.loads(handoff_data))
            
            # Only the initiating agent can cancel
            if handoff_request.from_agent_id != agent_id:
                raise ValueError(f"Only the initiating agent can cancel handoff {handoff_id}")
            
            # Check if already responded to
            response_data = await self.redis_client.hget("handoff_responses", handoff_id)
            if response_data:
                raise ValueError(f"Cannot cancel handoff {handoff_id} - already responded to")
            
            now = datetime.utcnow()
            
            # Update status to cancelled
            await self.redis_client.hset(
                "handoff_status",
                handoff_id,
                json.dumps({
                    "status": HandoffStatus.CANCELLED,
                    "updated_at": now.isoformat(),
                    "updated_by": agent_id,
                    "reason": reason
                })
            )
            
            # Remove from pending handoffs
            await self.redis_client.zrem(f"pending_handoffs:{handoff_request.to_agent_id}", handoff_id)
            
            # Create audit entry
            await self._create_audit_entry(
                handoff_id=handoff_id,
                event_type="cancelled",
                agent_id=agent_id,
                details={"reason": reason} if reason else {}
            )
            
            # Notify target agent
            await self.message_bus.send_message(
                sender_id=agent_id,
                receiver_id=handoff_request.to_agent_id,
                content=f"Handoff request cancelled: {reason or 'No reason provided'}",
                message_type=MessageType.HANDOFF,
                metadata={
                    "handoff_id": handoff_id,
                    "cancelled": True,
                    "response_type": "handoff_cancelled"
                }
            )
            
            logger.info(f"Handoff {handoff_id} cancelled by {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel handoff {handoff_id}: {e}")
            return False
    
    async def get_pending_handoffs(
        self,
        agent_id: str,
        limit: int = 50
    ) -> List[HandoffRequest]:
        """Get pending handoff requests for an agent."""
        if not self.redis_client:
            await self.connect()
        
        try:
            # Get handoff IDs sorted by priority (highest first)
            handoff_ids = await self.redis_client.zrevrange(
                f"pending_handoffs:{agent_id}",
                0, limit - 1
            )
            
            handoffs = []
            for handoff_id in handoff_ids:
                handoff_data = await self.redis_client.hget("handoff_requests", handoff_id)
                if handoff_data:
                    handoff = HandoffRequest(**json.loads(handoff_data))
                    
                    # Check if expired
                    if handoff.expires_at and datetime.utcnow() > handoff.expires_at:
                        await self._expire_handoff(handoff_id, handoff)
                        continue
                    
                    handoffs.append(handoff)
            
            return handoffs
            
        except Exception as e:
            logger.error(f"Failed to get pending handoffs for {agent_id}: {e}")
            return []
    
    async def get_handoff_history(
        self,
        agent_id: str,
        limit: int = 50
    ) -> List[HandoffSummary]:
        """Get handoff history for an agent."""
        if not self.redis_client:
            await self.connect()
        
        try:
            # Get handoffs where agent was involved
            pattern = f"*{agent_id}*"
            handoff_keys = await self.redis_client.scan_iter(
                match=f"handoff_requests:*",
                count=1000
            )
            
            summaries = []
            async for key in handoff_keys:
                handoff_id = key.split(":")[-1]
                summary = await self._create_handoff_summary(handoff_id)
                if summary and (summary.from_agent_id == agent_id or summary.to_agent_id == agent_id):
                    summaries.append(summary)
            
            # Sort by creation time, most recent first
            summaries.sort(key=lambda s: s.created_at, reverse=True)
            return summaries[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get handoff history for {agent_id}: {e}")
            return []
    
    async def get_handoff_audit(
        self,
        handoff_id: str
    ) -> List[HandoffAuditEntry]:
        """Get audit trail for a handoff."""
        if not self.redis_client:
            await self.connect()
        
        try:
            audit_data = await self.redis_client.lrange(f"handoff_audit:{handoff_id}", 0, -1)
            
            audit_entries = []
            for entry_data in audit_data:
                audit_entries.append(HandoffAuditEntry(**json.loads(entry_data)))
            
            return sorted(audit_entries, key=lambda e: e.timestamp)
            
        except Exception as e:
            logger.error(f"Failed to get handoff audit for {handoff_id}: {e}")
            return []
    
    async def _transfer_context(self, handoff_request: HandoffRequest) -> bool:
        """Transfer context data during handoff."""
        try:
            # Transfer conversation context if specified
            if handoff_request.conversation_id:
                # Grant access to conversation context
                await self.context_manager.grant_access(
                    key="*",  # All keys in conversation
                    scope=ContextScope.CONVERSATION,
                    scope_id=handoff_request.conversation_id,
                    agent_id=handoff_request.to_agent_id,
                    access_level="write",
                    granted_by=handoff_request.from_agent_id
                )
            
            # Transfer specific context data
            for key, value in handoff_request.context_data.items():
                await self.context_manager.set_context(
                    key=f"handoff_{key}",
                    value=value,
                    scope=ContextScope.AGENT,
                    scope_id=handoff_request.to_agent_id,
                    created_by=handoff_request.from_agent_id,
                    metadata={
                        "transferred_from": handoff_request.from_agent_id,
                        "handoff_id": handoff_request.id
                    },
                    change_reason=f"Transferred via handoff {handoff_request.id}"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to transfer context for handoff {handoff_request.id}: {e}")
            return False
    
    async def _complete_handoff(self, handoff_id: str, handoff_request: HandoffRequest) -> None:
        """Mark handoff as completed."""
        now = datetime.utcnow()
        
        await self.redis_client.hset(
            "handoff_status",
            handoff_id,
            json.dumps({
                "status": HandoffStatus.COMPLETED,
                "updated_at": now.isoformat(),
                "completed_by": handoff_request.to_agent_id
            })
        )
        
        await self._create_audit_entry(
            handoff_id=handoff_id,
            event_type="completed",
            agent_id=handoff_request.to_agent_id,
            details={
                "duration_seconds": (now - handoff_request.created_at).total_seconds()
            }
        )
    
    async def _expire_handoff(self, handoff_id: str, handoff_request: HandoffRequest) -> None:
        """Mark handoff as expired."""
        now = datetime.utcnow()
        
        await self.redis_client.hset(
            "handoff_status",
            handoff_id,
            json.dumps({
                "status": HandoffStatus.EXPIRED,
                "updated_at": now.isoformat(),
                "expired_at": now.isoformat()
            })
        )
        
        # Remove from pending
        await self.redis_client.zrem(f"pending_handoffs:{handoff_request.to_agent_id}", handoff_id)
        
        await self._create_audit_entry(
            handoff_id=handoff_id,
            event_type="expired",
            agent_id="system",
            details={"expired_at": now.isoformat()}
        )
    
    async def _create_audit_entry(
        self,
        handoff_id: str,
        event_type: str,
        agent_id: str,
        details: Dict[str, Any] = None
    ) -> None:
        """Create an audit entry for a handoff event."""
        audit_entry = HandoffAuditEntry(
            id=str(uuid4()),
            handoff_id=handoff_id,
            event_type=event_type,
            agent_id=agent_id,
            timestamp=datetime.utcnow(),
            details=details or {}
        )
        
        await self.redis_client.lpush(
            f"handoff_audit:{handoff_id}",
            audit_entry.model_dump_json()
        )
    
    async def _create_handoff_summary(self, handoff_id: str) -> Optional[HandoffSummary]:
        """Create a summary for a handoff."""
        try:
            # Get handoff request
            handoff_data = await self.redis_client.hget("handoff_requests", handoff_id)
            if not handoff_data:
                return None
            
            handoff_request = HandoffRequest(**json.loads(handoff_data))
            
            # Get status
            status_data = await self.redis_client.hget("handoff_status", handoff_id)
            status_info = json.loads(status_data) if status_data else {"status": HandoffStatus.INITIATED}
            
            # Calculate duration if completed
            completed_at = None
            duration_seconds = None
            
            if status_info["status"] == HandoffStatus.COMPLETED:
                completed_at = datetime.fromisoformat(status_info["updated_at"])
                duration_seconds = (completed_at - handoff_request.created_at).total_seconds()
            
            return HandoffSummary(
                handoff_id=handoff_id,
                from_agent_id=handoff_request.from_agent_id,
                to_agent_id=handoff_request.to_agent_id,
                reason=handoff_request.reason,
                status=status_info["status"],
                created_at=handoff_request.created_at,
                completed_at=completed_at,
                duration_seconds=duration_seconds,
                context_transferred=len(handoff_request.context_data) > 0,
                conversation_id=handoff_request.conversation_id
            )
            
        except Exception as e:
            logger.error(f"Failed to create handoff summary for {handoff_id}: {e}")
            return None


# Global handoff manager instance
_handoff_manager: Optional[HandoffManager] = None


def get_handoff_manager() -> HandoffManager:
    """Get or create the global handoff manager instance."""
    global _handoff_manager
    if _handoff_manager is None:
        _handoff_manager = HandoffManager()
    return _handoff_manager
