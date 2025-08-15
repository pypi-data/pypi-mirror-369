"""Permission and role-based access control system."""

from enum import Enum
from typing import List, Set, Optional
from functools import wraps

from fastapi import HTTPException, status, Depends
from pydantic import BaseModel

from .auth import get_current_user, User, APIKey


class Permission(str, Enum):
    """System permissions."""
    # Agent management
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_START = "agent:start"
    AGENT_STOP = "agent:stop"
    
    # Messaging
    MESSAGE_SEND = "message:send"
    MESSAGE_READ = "message:read"
    MESSAGE_BROADCAST = "message:broadcast"
    
    # Context management
    CONTEXT_READ = "context:read"
    CONTEXT_WRITE = "context:write"
    CONTEXT_DELETE = "context:delete"
    CONTEXT_ADMIN = "context:admin"
    
    # Handoffs
    HANDOFF_INITIATE = "handoff:initiate"
    HANDOFF_RESPOND = "handoff:respond"
    HANDOFF_CANCEL = "handoff:cancel"
    HANDOFF_ADMIN = "handoff:admin"
    
    # System administration
    SYSTEM_ADMIN = "system:admin"
    USER_ADMIN = "user:admin"
    API_KEY_ADMIN = "apikey:admin"
    
    # Monitoring
    METRICS_READ = "metrics:read"
    HEALTH_READ = "health:read"
    LOGS_READ = "logs:read"
    
    # Workflows
    WORKFLOW_CREATE = "workflow:create"
    WORKFLOW_EXECUTE = "workflow:execute"
    WORKFLOW_ADMIN = "workflow:admin"


class Role(str, Enum):
    """System roles with predefined permissions."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    AGENT_OPERATOR = "agent_operator"
    VIEWER = "viewer"


# Role-to-permissions mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        # All permissions
        Permission.AGENT_CREATE, Permission.AGENT_READ, Permission.AGENT_UPDATE, 
        Permission.AGENT_DELETE, Permission.AGENT_START, Permission.AGENT_STOP,
        Permission.MESSAGE_SEND, Permission.MESSAGE_READ, Permission.MESSAGE_BROADCAST,
        Permission.CONTEXT_READ, Permission.CONTEXT_WRITE, Permission.CONTEXT_DELETE, Permission.CONTEXT_ADMIN,
        Permission.HANDOFF_INITIATE, Permission.HANDOFF_RESPOND, Permission.HANDOFF_CANCEL, Permission.HANDOFF_ADMIN,
        Permission.SYSTEM_ADMIN, Permission.USER_ADMIN, Permission.API_KEY_ADMIN,
        Permission.METRICS_READ, Permission.HEALTH_READ, Permission.LOGS_READ,
        Permission.WORKFLOW_CREATE, Permission.WORKFLOW_EXECUTE, Permission.WORKFLOW_ADMIN,
    ],
    
    Role.DEVELOPER: [
        # Agent and workflow management
        Permission.AGENT_CREATE, Permission.AGENT_READ, Permission.AGENT_UPDATE, Permission.AGENT_START, Permission.AGENT_STOP,
        Permission.MESSAGE_SEND, Permission.MESSAGE_READ, Permission.MESSAGE_BROADCAST,
        Permission.CONTEXT_READ, Permission.CONTEXT_WRITE,
        Permission.HANDOFF_INITIATE, Permission.HANDOFF_RESPOND, Permission.HANDOFF_CANCEL,
        Permission.METRICS_READ, Permission.HEALTH_READ,
        Permission.WORKFLOW_CREATE, Permission.WORKFLOW_EXECUTE,
    ],
    
    Role.AGENT_OPERATOR: [
        # Agent operations only
        Permission.AGENT_READ, Permission.AGENT_START, Permission.AGENT_STOP,
        Permission.MESSAGE_SEND, Permission.MESSAGE_READ,
        Permission.CONTEXT_READ, Permission.CONTEXT_WRITE,
        Permission.HANDOFF_INITIATE, Permission.HANDOFF_RESPOND,
        Permission.HEALTH_READ,
        Permission.WORKFLOW_EXECUTE,
    ],
    
    Role.USER: [
        # Basic usage
        Permission.AGENT_READ,
        Permission.MESSAGE_SEND, Permission.MESSAGE_READ,
        Permission.CONTEXT_READ,
        Permission.HANDOFF_INITIATE, Permission.HANDOFF_RESPOND,
        Permission.HEALTH_READ,
    ],
    
    Role.VIEWER: [
        # Read-only access
        Permission.AGENT_READ,
        Permission.MESSAGE_READ,
        Permission.CONTEXT_READ,
        Permission.HEALTH_READ,
        Permission.METRICS_READ,
    ],
}


class PermissionChecker:
    """Check permissions for users and API keys."""
    
    @staticmethod
    def get_user_permissions(user: User) -> Set[Permission]:
        """Get all permissions for a user based on their roles."""
        permissions = set()
        
        for role in user.roles:
            if role in ROLE_PERMISSIONS:
                permissions.update(ROLE_PERMISSIONS[role])
        
        return permissions
    
    @staticmethod
    def get_api_key_permissions(api_key: APIKey) -> Set[Permission]:
        """Get all permissions for an API key."""
        return set(api_key.permissions)
    
    @staticmethod
    def check_user_permission(user: User, permission: Permission) -> bool:
        """Check if a user has a specific permission."""
        user_permissions = PermissionChecker.get_user_permissions(user)
        return permission in user_permissions
    
    @staticmethod
    def check_api_key_permission(api_key: APIKey, permission: Permission) -> bool:
        """Check if an API key has a specific permission."""
        api_key_permissions = PermissionChecker.get_api_key_permissions(api_key)
        return permission in api_key_permissions


def require_permission(permission: Permission):
    """Decorator to require a specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get user from kwargs (injected by dependency)
            user = kwargs.get('current_user')
            api_key = kwargs.get('api_key')
            
            has_permission = False
            
            if user and PermissionChecker.check_user_permission(user, permission):
                has_permission = True
            elif api_key and PermissionChecker.check_api_key_permission(api_key, permission):
                has_permission = True
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class PermissionDependency:
    """FastAPI dependency for permission checking."""
    
    def __init__(self, required_permission: Permission):
        self.required_permission = required_permission
    
    async def __call__(self, user: Optional[User] = Depends(get_current_user)) -> bool:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if not PermissionChecker.check_user_permission(user, self.required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {self.required_permission}"
            )
        
        return True


async def check_agent_access(agent_id: str, user: User, required_permission: Permission) -> bool:
    """Check if a user has permission to access a specific agent."""
    # For now, implement basic permission checking
    # This can be extended to include agent-specific ownership/access rules
    
    if not PermissionChecker.check_user_permission(user, required_permission):
        return False
    
    # Additional agent-specific access checks can be added here
    # For example:
    # - Check if user owns the agent
    # - Check if agent is in user's allowed groups
    # - Check agent visibility settings
    
    return True


# Convenience functions for common permission checks
def require_agent_read():
    """Require agent read permission."""
    return PermissionDependency(Permission.AGENT_READ)


def require_agent_write():
    """Require agent write permission."""
    return PermissionDependency(Permission.AGENT_CREATE)


def require_message_send():
    """Require message send permission."""
    return PermissionDependency(Permission.MESSAGE_SEND)


def require_context_write():
    """Require context write permission."""
    return PermissionDependency(Permission.CONTEXT_WRITE)


def require_handoff_permission():
    """Require handoff permission."""
    return PermissionDependency(Permission.HANDOFF_INITIATE)


def require_admin():
    """Require admin permission."""
    return PermissionDependency(Permission.SYSTEM_ADMIN)


# Permission validation models
class PermissionRequest(BaseModel):
    """Request to check permissions."""
    permissions: List[Permission]


class PermissionResponse(BaseModel):
    """Response with permission check results."""
    permissions: List[Permission]
    granted: List[Permission]
    denied: List[Permission]
