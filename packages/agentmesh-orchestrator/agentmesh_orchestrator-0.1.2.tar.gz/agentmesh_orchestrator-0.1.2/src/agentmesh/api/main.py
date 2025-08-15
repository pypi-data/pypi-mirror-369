"""FastAPI application setup for AutoGen A2A system."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .middleware import ErrorHandlingMiddleware, LoggingMiddleware
from .routers import agents, health, messaging, websocket, context, handoffs, auth, workflows
from ..core.config import get_settings
from ..db.database import init_db, close_db, create_tables
from ..messaging.message_bus import get_message_bus
from ..core.context_manager import get_context_manager
from ..core.handoff_manager import get_handoff_manager
from ..security import get_auth_manager, get_rate_limiter, RateLimitMiddleware
from ..monitoring import CorrelationIdMiddleware, get_metrics_collector, setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    settings = get_settings()
    logger.info("Starting AutoGen A2A API server...")
    
    # Setup enhanced logging
    setup_logging(level=settings.log_level)
    logger.info("Enhanced logging configured")
    
    # Initialize database
    init_db()
    await create_tables()
    logger.info("Database initialized")
    
    # Initialize Redis connections for messaging, context, handoffs, auth, and rate limiting
    try:
        message_bus = get_message_bus()
        await message_bus.connect()
        logger.info("Message bus connected")
        
        context_manager = get_context_manager()
        await context_manager.connect()
        logger.info("Context manager connected")
        
        handoff_manager = get_handoff_manager()
        await handoff_manager.connect()
        logger.info("Handoff manager connected")
        
        auth_manager = get_auth_manager()
        await auth_manager.connect()
        logger.info("Auth manager connected")
        
        rate_limiter = get_rate_limiter()
        await rate_limiter.connect()
        logger.info("Rate limiter connected")
        
        # Initialize metrics collection
        metrics_collector = get_metrics_collector()
        logger.info("Metrics collector initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize Redis services: {e}")
        raise
    
    # Initialize tracing - disabled for now
    # TODO: Add OpenTelemetry instrumentation
    
    yield
    
    # Shutdown
    logger.info("Shutting down AutoGen A2A API server...")
    
    # Close Redis connections
    try:
        await message_bus.disconnect()
        await context_manager.disconnect()
        await handoff_manager.disconnect()
        
        auth_manager = get_auth_manager()
        await auth_manager.disconnect()
        
        rate_limiter = get_rate_limiter()
        await rate_limiter.disconnect()
        
        logger.info("Redis connections closed")
    except Exception as e:
        logger.error(f"Error closing Redis connections: {e}")
    
    await close_db()
    logger.info("Database connections closed")


def create_app() -> FastAPI:
    """Create FastAPI application instance."""
    settings = get_settings()
    
    app = FastAPI(
        title="AutoGen A2A API",
        description="AutoGen Agent-to-Agent Communication System API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom middleware (order matters - correlation ID first, then rate limiting, then error handling)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    app.include_router(messaging.router, prefix="/api/v1", tags=["messaging"])
    app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])
    app.include_router(context.router, prefix="/api/v1", tags=["context"])
    app.include_router(handoffs.router, prefix="/api/v1", tags=["handoffs"])
    app.include_router(workflows.router, prefix="/api/v1", tags=["workflows"])
    
    # Exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception occurred")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "status_code": 500,
                "path": str(request.url.path)
            }
        )
    
    # Instrument with OpenTelemetry - disabled for now
    # TODO: Add OpenTelemetry instrumentation
    # if settings.enable_tracing:
    #     FastAPIInstrumentor.instrument_app(app)
    
    return app


# Create the application instance
app = create_app()
