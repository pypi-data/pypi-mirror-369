"""Authentication and authorization system for AutoGen A2A."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import uuid4

import redis.asyncio as redis
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..core.config import get_settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
bearer_scheme = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

settings = get_settings()


class User(BaseModel):
    """User model for authentication."""
    id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: List[str] = []
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None


class APIKey(BaseModel):
    """API Key model."""
    id: str
    name: str
    key_hash: str
    user_id: str
    permissions: List[str] = []
    is_active: bool = True
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class AuthManager:
    """Manages authentication and authorization."""
    
    def __init__(self):
        """Initialize auth manager."""
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        
    async def connect(self) -> None:
        """Connect to Redis for session storage."""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                db=self.settings.redis_db + 3,  # Use different DB for auth
                decode_responses=True
            )
            await self.redis_client.ping()
        except Exception as e:
            raise Exception(f"Failed to connect to Redis for auth: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
    
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm="HS256"
        )
        
        return encoded_jwt
    
    async def verify_token(self, token: str) -> Optional[User]:
        """Verify a JWT token and return the user."""
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=["HS256"]
            )
            
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            
            # Get user from Redis cache or database
            user = await self.get_user(user_id)
            return user
            
        except JWTError:
            return None
    
    async def create_api_key(
        self, 
        user_id: str, 
        name: str, 
        permissions: List[str] = None,
        expires_in_days: Optional[int] = None
    ) -> tuple[str, APIKey]:
        """Create a new API key for a user."""
        if not self.redis_client:
            await self.connect()
        
        # Generate API key
        raw_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        # Create API key object
        api_key = APIKey(
            id=str(uuid4()),
            name=name,
            key_hash=key_hash,
            user_id=user_id,
            permissions=permissions or [],
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days) if expires_in_days else None
        )
        
        # Store in Redis
        await self.redis_client.hset(
            "api_keys",
            api_key.id,
            api_key.model_dump_json()
        )
        
        # Index by hash for quick lookup
        await self.redis_client.set(f"api_key_hash:{key_hash}", api_key.id)
        
        return raw_key, api_key
    
    async def verify_api_key(self, key: str) -> Optional[APIKey]:
        """Verify an API key and return the API key object."""
        if not self.redis_client:
            await self.connect()
        
        try:
            # Hash the provided key
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            
            # Get API key ID from hash
            api_key_id = await self.redis_client.get(f"api_key_hash:{key_hash}")
            if not api_key_id:
                return None
            
            # Get API key data
            api_key_data = await self.redis_client.hget("api_keys", api_key_id)
            if not api_key_data:
                return None
            
            api_key = APIKey.model_validate_json(api_key_data)
            
            # Check if active and not expired
            if not api_key.is_active:
                return None
            
            if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
                return None
            
            # Update last used timestamp
            api_key.last_used = datetime.utcnow()
            await self.redis_client.hset(
                "api_keys",
                api_key_id,
                api_key.model_dump_json()
            )
            
            return api_key
            
        except Exception:
            return None
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        roles: List[str] = None
    ) -> User:
        """Create a new user."""
        if not self.redis_client:
            await self.connect()
        
        user = User(
            id=str(uuid4()),
            username=username,
            email=email,
            full_name=full_name,
            roles=roles or ["user"],
            created_at=datetime.utcnow()
        )
        
        # Store user
        await self.redis_client.hset(
            "users",
            user.id,
            user.model_dump_json()
        )
        
        # Store password hash separately
        password_hash = self.hash_password(password)
        await self.redis_client.set(f"user_password:{user.id}", password_hash)
        
        # Index by username
        await self.redis_client.set(f"username:{username}", user.id)
        
        return user
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        if not self.redis_client:
            await self.connect()
        
        user_data = await self.redis_client.hget("users", user_id)
        if user_data:
            return User.model_validate_json(user_data)
        return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        if not self.redis_client:
            await self.connect()
        
        user_id = await self.redis_client.get(f"username:{username}")
        if user_id:
            return await self.get_user(user_id)
        return None
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        if not self.redis_client:
            await self.connect()
        
        user = await self.get_user_by_username(username)
        if not user:
            return None
        
        # Get password hash
        password_hash = await self.redis_client.get(f"user_password:{user.id}")
        if not password_hash:
            return None
        
        # Verify password
        if not self.verify_password(password, password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.redis_client.hset(
            "users",
            user.id,
            user.model_dump_json()
        )
        
        return user


# Global auth manager
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get the global auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


# Authentication dependencies for FastAPI
class APIKeyAuth:
    """API Key authentication dependency."""
    
    def __init__(self, required_permissions: List[str] = None):
        self.required_permissions = required_permissions or []
    
    async def __call__(self, api_key: Optional[str] = Security(api_key_header)) -> Optional[APIKey]:
        if not api_key:
            if self.required_permissions:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key required"
                )
            return None
        
        auth_manager = get_auth_manager()
        api_key_obj = await auth_manager.verify_api_key(api_key)
        
        if not api_key_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Check permissions
        if self.required_permissions:
            missing_permissions = set(self.required_permissions) - set(api_key_obj.permissions)
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permissions: {', '.join(missing_permissions)}"
                )
        
        return api_key_obj


class TokenAuth:
    """JWT Token authentication dependency."""
    
    def __init__(self, required_roles: List[str] = None):
        self.required_roles = required_roles or []
    
    async def __call__(self, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> User:
        auth_manager = get_auth_manager()
        user = await auth_manager.verify_token(credentials.credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Check roles
        if self.required_roles:
            missing_roles = set(self.required_roles) - set(user.roles)
            if missing_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing roles: {', '.join(missing_roles)}"
                )
        
        return user


# Convenience functions
async def get_current_user(user: User = Depends(TokenAuth())) -> User:
    """Get the current authenticated user."""
    return user


async def get_current_admin_user(user: User = Depends(TokenAuth(required_roles=["admin"]))) -> User:
    """Get the current authenticated admin user."""
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token."""
    auth_manager = get_auth_manager()
    return auth_manager.create_access_token(data, expires_delta)


async def verify_token(token: str) -> Optional[User]:
    """Verify a token and return the user."""
    auth_manager = get_auth_manager()
    return await auth_manager.verify_token(token)
