"""Configuration management for AutoGen A2A system."""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    reload: bool = Field(default=False, env="API_RELOAD")
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./autogen_a2a.db", 
        env="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # Security & Authentication
    secret_key: str = Field(
        default="your-secret-key-change-in-production", 
        env="SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_hours: int = Field(default=24, env="ACCESS_TOKEN_EXPIRE_HOURS")
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    allowed_api_keys: List[str] = Field(default_factory=list, env="ALLOWED_API_KEYS")
    
    # Rate Limiting
    enable_rate_limiting: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    default_rate_limit_per_minute: int = Field(default=300, env="DEFAULT_RATE_LIMIT_PER_MINUTE")
    default_rate_limit_per_hour: int = Field(default=5000, env="DEFAULT_RATE_LIMIT_PER_HOUR")
    
    # Password Security
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    password_hash_rounds: int = Field(default=12, env="PASSWORD_HASH_ROUNDS")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"], 
        env="CORS_ORIGINS"
    )
    
    # Observability
    enable_tracing: bool = Field(default=False, env="ENABLE_TRACING")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_docs: bool = Field(default=True, env="ENABLE_DOCS")
    
    # Jaeger Configuration
    jaeger_host: str = Field(default="localhost", env="JAEGER_HOST")
    jaeger_port: int = Field(default=6832, env="JAEGER_PORT")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Agent Configuration
    default_model: str = Field(default="gpt-4o", env="DEFAULT_MODEL")
    max_agents: int = Field(default=100, env="MAX_AGENTS")
    agent_timeout: int = Field(default=300, env="AGENT_TIMEOUT")  # seconds
    
    # Workflow Configuration
    max_workflows: int = Field(default=50, env="MAX_WORKFLOWS")
    workflow_timeout: int = Field(default=3600, env="WORKFLOW_TIMEOUT")  # seconds
    
    # Message Bus Configuration
    message_retention_hours: int = Field(default=24, env="MESSAGE_RETENTION_HOURS")
    max_message_size: int = Field(default=1024 * 1024, env="MAX_MESSAGE_SIZE")  # 1MB
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def get_environment() -> str:
    """Get current environment name."""
    return os.getenv("ENVIRONMENT", "development")
