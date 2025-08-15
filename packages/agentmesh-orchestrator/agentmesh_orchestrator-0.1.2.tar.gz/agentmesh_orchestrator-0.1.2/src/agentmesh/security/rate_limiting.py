"""Rate limiting middleware and utilities for AutoGen A2A."""

import time
from typing import Dict, Optional, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum

import redis.asyncio as redis
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import get_settings


class RateLimitType(str, Enum):
    """Rate limit types."""
    PER_SECOND = "per_second"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"


class RateLimitConfig:
    """Rate limit configuration."""
    
    def __init__(
        self,
        requests_per_second: Optional[int] = None,
        requests_per_minute: Optional[int] = None,
        requests_per_hour: Optional[int] = None,
        requests_per_day: Optional[int] = None,
        burst_size: Optional[int] = None,
    ):
        self.requests_per_second = requests_per_second
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.burst_size = burst_size or (requests_per_second * 2 if requests_per_second else None)


class RateLimiter:
    """Redis-based rate limiter using sliding window algorithm."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        
        # Default rate limits
        self.default_limits = RateLimitConfig(
            requests_per_second=10,
            requests_per_minute=300,
            requests_per_hour=5000,
            requests_per_day=50000,
            burst_size=20
        )
        
        # Per-endpoint rate limits
        self.endpoint_limits: Dict[str, RateLimitConfig] = {
            # High-frequency endpoints
            "/api/v1/health": RateLimitConfig(requests_per_second=100, requests_per_minute=1000),
            "/api/v1/agents/*/status": RateLimitConfig(requests_per_second=50, requests_per_minute=1000),
            
            # Messaging endpoints
            "/api/v1/messaging/send": RateLimitConfig(requests_per_second=5, requests_per_minute=100),
            "/api/v1/messaging/broadcast": RateLimitConfig(requests_per_second=1, requests_per_minute=10),
            
            # Agent management
            "/api/v1/agents/create": RateLimitConfig(requests_per_minute=20, requests_per_hour=100),
            "/api/v1/agents/*/start": RateLimitConfig(requests_per_minute=30, requests_per_hour=200),
            "/api/v1/agents/*/stop": RateLimitConfig(requests_per_minute=30, requests_per_hour=200),
            
            # Context operations
            "/api/v1/context/set": RateLimitConfig(requests_per_second=10, requests_per_minute=300),
            "/api/v1/context/get": RateLimitConfig(requests_per_second=20, requests_per_minute=600),
            
            # Handoffs
            "/api/v1/handoffs/initiate": RateLimitConfig(requests_per_minute=50, requests_per_hour=500),
            "/api/v1/handoffs/respond": RateLimitConfig(requests_per_minute=100, requests_per_hour=1000),
        }
        
        # Per-user type rate limits
        self.user_type_limits: Dict[str, RateLimitConfig] = {
            "admin": RateLimitConfig(
                requests_per_second=50,
                requests_per_minute=1000,
                requests_per_hour=20000,
                requests_per_day=200000,
            ),
            "developer": RateLimitConfig(
                requests_per_second=20,
                requests_per_minute=500,
                requests_per_hour=10000,
                requests_per_day=100000,
            ),
            "user": RateLimitConfig(
                requests_per_second=10,
                requests_per_minute=300,
                requests_per_hour=5000,
                requests_per_day=50000,
            ),
            "viewer": RateLimitConfig(
                requests_per_second=5,
                requests_per_minute=150,
                requests_per_hour=2000,
                requests_per_day=20000,
            ),
        }
    
    async def connect(self) -> None:
        """Connect to Redis for rate limiting."""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                db=self.settings.redis_db + 4,  # Use different DB for rate limiting
                decode_responses=True
            )
            await self.redis_client.ping()
        except Exception as e:
            raise Exception(f"Failed to connect to Redis for rate limiting: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
    
    def _get_window_key(self, identifier: str, window_type: RateLimitType, window_start: int) -> str:
        """Generate a Redis key for a specific window."""
        return f"rate_limit:{identifier}:{window_type}:{window_start}"
    
    async def _check_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        window_type: RateLimitType
    ) -> Tuple[bool, int, int]:
        """
        Check rate limit using sliding window algorithm.
        
        Returns:
            (allowed, current_count, reset_time)
        """
        if not self.redis_client:
            await self.connect()
        
        now = int(time.time())
        window_start = now - (now % window_seconds)
        prev_window_start = window_start - window_seconds
        
        current_key = self._get_window_key(identifier, window_type, window_start)
        prev_key = self._get_window_key(identifier, window_type, prev_window_start)
        
        # Use pipeline for atomic operations
        pipe = self.redis_client.pipeline()
        
        # Get current and previous window counts
        pipe.get(current_key)
        pipe.get(prev_key)
        
        results = await pipe.execute()
        current_count = int(results[0] or 0)
        prev_count = int(results[1] or 0)
        
        # Calculate weighted count using sliding window
        elapsed_in_current_window = now - window_start
        weight = elapsed_in_current_window / window_seconds
        weighted_count = (prev_count * (1 - weight)) + current_count
        
        # Check if limit exceeded
        if weighted_count >= limit:
            reset_time = window_start + window_seconds
            return False, int(weighted_count), reset_time
        
        # Increment current window counter
        pipe = self.redis_client.pipeline()
        pipe.incr(current_key)
        pipe.expire(current_key, window_seconds * 2)  # Keep for 2 windows
        await pipe.execute()
        
        reset_time = window_start + window_seconds
        return True, int(weighted_count) + 1, reset_time
    
    async def check_rate_limit(
        self,
        identifier: str,
        endpoint: Optional[str] = None,
        user_type: Optional[str] = None
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check rate limit for an identifier.
        
        Returns:
            (allowed, metadata)
        """
        # Determine which limits to apply
        config = self.default_limits
        
        if user_type and user_type in self.user_type_limits:
            config = self.user_type_limits[user_type]
        
        if endpoint:
            # Match endpoint patterns
            for pattern, limit_config in self.endpoint_limits.items():
                if self._match_endpoint_pattern(endpoint, pattern):
                    config = limit_config
                    break
        
        # Check all configured limits
        limits_to_check = []
        
        if config.requests_per_second:
            limits_to_check.append((config.requests_per_second, 1, RateLimitType.PER_SECOND))
        if config.requests_per_minute:
            limits_to_check.append((config.requests_per_minute, 60, RateLimitType.PER_MINUTE))
        if config.requests_per_hour:
            limits_to_check.append((config.requests_per_hour, 3600, RateLimitType.PER_HOUR))
        if config.requests_per_day:
            limits_to_check.append((config.requests_per_day, 86400, RateLimitType.PER_DAY))
        
        metadata = {
            "identifier": identifier,
            "endpoint": endpoint,
            "user_type": user_type,
            "limits": {},
            "allowed": True,
            "retry_after": None
        }
        
        # Check each limit
        for limit, window_seconds, window_type in limits_to_check:
            allowed, current_count, reset_time = await self._check_limit(
                identifier, limit, window_seconds, window_type
            )
            
            metadata["limits"][window_type] = {
                "limit": limit,
                "current": current_count,
                "remaining": max(0, limit - current_count),
                "reset_time": reset_time
            }
            
            if not allowed:
                metadata["allowed"] = False
                metadata["retry_after"] = reset_time - int(time.time())
                metadata["violated_limit"] = window_type
                break
        
        return metadata["allowed"], metadata
    
    def _match_endpoint_pattern(self, endpoint: str, pattern: str) -> bool:
        """Match endpoint against pattern (supports wildcards)."""
        if "*" not in pattern:
            return endpoint == pattern
        
        # Simple wildcard matching
        parts = pattern.split("*")
        if len(parts) == 2:
            prefix, suffix = parts
            return endpoint.startswith(prefix) and endpoint.endswith(suffix)
        
        # For more complex patterns, can be extended
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for FastAPI."""
    
    def __init__(self, app, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.exempt_paths = {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        }
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client."""
        # Try to get authenticated user/API key
        user_id = getattr(request.state, "user_id", None)
        api_key_id = getattr(request.state, "api_key_id", None)
        
        if user_id:
            return f"user:{user_id}"
        elif api_key_id:
            return f"api_key:{api_key_id}"
        else:
            # Fall back to IP address
            client_ip = request.client.host
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()
            return f"ip:{client_ip}"
    
    def _get_user_type(self, request: Request) -> Optional[str]:
        """Get user type from request state."""
        return getattr(request.state, "user_type", None)
    
    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiting."""
        # Skip rate limiting for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # Get client identifier and metadata
        identifier = self._get_client_identifier(request)
        endpoint = request.url.path
        user_type = self._get_user_type(request)
        
        try:
            # Check rate limit
            allowed, metadata = await self.rate_limiter.check_rate_limit(
                identifier=identifier,
                endpoint=endpoint,
                user_type=user_type
            )
            
            if not allowed:
                # Rate limit exceeded
                response_data = {
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests for {metadata.get('violated_limit', 'unknown')} limit",
                    "retry_after": metadata.get("retry_after"),
                    "limits": metadata.get("limits", {})
                }
                
                headers = {}
                if metadata.get("retry_after"):
                    headers["Retry-After"] = str(metadata["retry_after"])
                
                # Add rate limit headers
                for limit_type, limit_info in metadata.get("limits", {}).items():
                    headers[f"X-RateLimit-{limit_type.replace('_', '-')}-Limit"] = str(limit_info["limit"])
                    headers[f"X-RateLimit-{limit_type.replace('_', '-')}-Remaining"] = str(limit_info["remaining"])
                    headers[f"X-RateLimit-{limit_type.replace('_', '-')}-Reset"] = str(limit_info["reset_time"])
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=response_data,
                    headers=headers
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to successful responses
            for limit_type, limit_info in metadata.get("limits", {}).items():
                response.headers[f"X-RateLimit-{limit_type.replace('_', '-')}-Limit"] = str(limit_info["limit"])
                response.headers[f"X-RateLimit-{limit_type.replace('_', '-')}-Remaining"] = str(limit_info["remaining"])
                response.headers[f"X-RateLimit-{limit_type.replace('_', '-')}-Reset"] = str(limit_info["reset_time"])
            
            return response
            
        except Exception as e:
            # If rate limiting fails, allow the request but log the error
            print(f"Rate limiting error: {e}")
            return await call_next(request)


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# Decorator for manual rate limiting
def rate_limit(
    requests_per_second: Optional[int] = None,
    requests_per_minute: Optional[int] = None,
    requests_per_hour: Optional[int] = None,
    requests_per_day: Optional[int] = None,
):
    """Decorator to apply rate limiting to specific endpoints."""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # This would need to be integrated with the FastAPI dependency system
            # For now, it's a placeholder for potential future use
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Administrative functions
async def reset_rate_limit(identifier: str, rate_limiter: Optional[RateLimiter] = None) -> bool:
    """Reset rate limits for a specific identifier."""
    if not rate_limiter:
        rate_limiter = get_rate_limiter()
    
    if not rate_limiter.redis_client:
        await rate_limiter.connect()
    
    try:
        # Find and delete all rate limit keys for this identifier
        pattern = f"rate_limit:{identifier}:*"
        keys = await rate_limiter.redis_client.keys(pattern)
        
        if keys:
            await rate_limiter.redis_client.delete(*keys)
        
        return True
    except Exception:
        return False


async def get_rate_limit_status(identifier: str, rate_limiter: Optional[RateLimiter] = None) -> Dict:
    """Get current rate limit status for an identifier."""
    if not rate_limiter:
        rate_limiter = get_rate_limiter()
    
    # This will check limits without incrementing counters
    # Implementation would need to be added to check current status
    return {
        "identifier": identifier,
        "status": "active",
        "limits": {}
    }
