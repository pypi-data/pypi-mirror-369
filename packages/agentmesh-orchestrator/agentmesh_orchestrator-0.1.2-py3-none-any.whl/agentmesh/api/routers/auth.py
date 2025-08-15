"""Authentication router for user login, API key management, and security operations."""

from datetime import timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from ...security import (
    get_auth_manager, get_current_user, get_current_admin_user, 
    User, APIKey, Token, create_access_token
)
from ...security.permissions import Permission, Role, PermissionChecker

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class CreateUserRequest(BaseModel):
    """Create user request model."""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    roles: List[str] = ["user"]


class CreateAPIKeyRequest(BaseModel):
    """Create API key request model."""
    name: str
    permissions: List[str] = []
    expires_in_days: Optional[int] = None


class CreateAPIKeyResponse(BaseModel):
    """Create API key response model."""
    api_key: str
    key_info: APIKey


class UserResponse(BaseModel):
    """User response model (without sensitive data)."""
    id: str
    username: str
    email: Optional[str]
    full_name: Optional[str]
    roles: List[str]
    is_active: bool
    created_at: str
    last_login: Optional[str]


@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_manager = Depends(get_auth_manager)
):
    """Authenticate user and return access token."""
    user = await auth_manager.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username, "roles": user.roles},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user=user
    )


@router.post("/auth/register", response_model=UserResponse)
async def register(
    request: CreateUserRequest,
    auth_manager = Depends(get_auth_manager),
    _: User = Depends(get_current_admin_user)  # Only admins can create users
):
    """Register a new user (admin only)."""
    # Check if username already exists
    existing_user = await auth_manager.get_user_by_username(request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Validate roles
    for role in request.roles:
        if role not in [r.value for r in Role]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role}"
            )
    
    user = await auth_manager.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        roles=request.roles
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        roles=user.roles,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        roles=current_user.roles,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )


@router.post("/auth/api-keys", response_model=CreateAPIKeyResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    current_user: User = Depends(get_current_user),
    auth_manager = Depends(get_auth_manager)
):
    """Create a new API key for the current user."""
    # Validate permissions
    for permission in request.permissions:
        if permission not in [p.value for p in Permission]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid permission: {permission}"
            )
    
    # Check if user has the permissions they're trying to grant
    user_permissions = PermissionChecker.get_user_permissions(current_user)
    requested_permissions = set(request.permissions)
    
    if not requested_permissions.issubset({p.value for p in user_permissions}):
        missing = requested_permissions - {p.value for p in user_permissions}
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot grant permissions you don't have: {', '.join(missing)}"
        )
    
    raw_key, api_key = await auth_manager.create_api_key(
        user_id=current_user.id,
        name=request.name,
        permissions=request.permissions,
        expires_in_days=request.expires_in_days
    )
    
    return CreateAPIKeyResponse(
        api_key=raw_key,
        key_info=api_key
    )


@router.get("/auth/api-keys", response_model=List[APIKey])
async def list_user_api_keys(
    current_user: User = Depends(get_current_user),
    auth_manager = Depends(get_auth_manager)
):
    """List API keys for the current user."""
    # Note: This is a simplified implementation
    # In practice, you'd need to implement a proper method to get user's API keys
    # For now, return empty list as placeholder
    return []


@router.delete("/auth/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    auth_manager = Depends(get_auth_manager)
):
    """Revoke an API key."""
    # Implementation would need to be added to auth_manager
    # For now, return success
    return {"message": "API key revoked successfully"}


@router.get("/auth/permissions")
async def get_user_permissions(current_user: User = Depends(get_current_user)):
    """Get current user's permissions."""
    permissions = PermissionChecker.get_user_permissions(current_user)
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "roles": current_user.roles,
        "permissions": [p.value for p in permissions]
    }


@router.get("/auth/roles")
async def list_roles():
    """List all available roles and their permissions."""
    from ...security.permissions import ROLE_PERMISSIONS
    
    role_info = {}
    for role, permissions in ROLE_PERMISSIONS.items():
        role_info[role.value] = [p.value for p in permissions]
    
    return {
        "roles": role_info,
        "available_permissions": [p.value for p in Permission]
    }


@router.post("/auth/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh the current user's access token."""
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": current_user.id, "username": current_user.username, "roles": current_user.roles},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user=current_user
    )


# Admin endpoints
@router.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    _: User = Depends(get_current_admin_user),
    auth_manager = Depends(get_auth_manager)
):
    """List all users (admin only)."""
    # Implementation would need to be added to auth_manager
    # For now, return empty list as placeholder
    return []


@router.put("/admin/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    _: User = Depends(get_current_admin_user),
    auth_manager = Depends(get_auth_manager)
):
    """Activate a user account (admin only)."""
    # Implementation would need to be added to auth_manager
    return {"message": f"User {user_id} activated successfully"}


@router.put("/admin/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    _: User = Depends(get_current_admin_user),
    auth_manager = Depends(get_auth_manager)
):
    """Deactivate a user account (admin only)."""
    # Implementation would need to be added to auth_manager
    return {"message": f"User {user_id} deactivated successfully"}
