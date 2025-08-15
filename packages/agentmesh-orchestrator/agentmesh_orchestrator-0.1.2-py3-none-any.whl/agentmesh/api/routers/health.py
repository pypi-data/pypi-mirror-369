"""Health check endpoints with comprehensive monitoring."""

from typing import Dict, List

from fastapi import APIRouter, status, HTTPException, Response
from pydantic import BaseModel

from ...core.config import get_settings
from ...monitoring import (
    get_health_checker, get_metrics_collector, 
    HealthStatus, ComponentHealth, SystemHealth,
    PROMETHEUS_CONTENT_TYPE
)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str
    version: str
    environment: str
    timestamp: str
    uptime_seconds: float
    message: str
    components: List[ComponentHealth]


class ReadinessResponse(BaseModel):
    """Readiness check response model."""
    
    ready: bool
    message: str
    critical_components: List[str]


class LivenessResponse(BaseModel):
    """Liveness check response model."""
    
    alive: bool
    uptime_seconds: float


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Comprehensive Health Check",
    description="Check the health status of all system components"
)
async def health_check(detailed: bool = False) -> HealthResponse:
    """Perform comprehensive health check."""
    from ...core.config import get_environment
    
    health_checker = get_health_checker()
    system_health = await health_checker.get_system_health(force_check=detailed)
    
    # Map health status to HTTP status
    if system_health.status == HealthStatus.UNHEALTHY:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif system_health.status == HealthStatus.DEGRADED:
        status_code = status.HTTP_200_OK  # Still functional
    else:
        status_code = status.HTTP_200_OK
    
    return HealthResponse(
        status=system_health.status.value,
        version=system_health.version,
        environment=get_environment(),
        timestamp=system_health.timestamp.isoformat(),
        uptime_seconds=system_health.uptime_seconds,
        message=system_health.message,
        components=system_health.components
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness Check",
    description="Check if the API server is ready to handle requests"
)
async def readiness_check() -> ReadinessResponse:
    """Perform readiness check for Kubernetes/container orchestration."""
    health_checker = get_health_checker()
    ready = health_checker.get_readiness_probe()
    
    if not ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )
    
    critical_components = [
        name for name, config in health_checker.check_configs.items()
        if config.get("critical", True)
    ]
    
    return ReadinessResponse(
        ready=ready,
        message="Service is ready to handle requests",
        critical_components=critical_components
    )


@router.get(
    "/live",
    response_model=LivenessResponse,
    summary="Liveness Check", 
    description="Check if the API server is alive (for Kubernetes liveness probe)"
)
async def liveness_check() -> LivenessResponse:
    """Perform liveness check for Kubernetes/container orchestration."""
    health_checker = get_health_checker()
    alive = health_checker.get_liveness_probe()
    
    if not alive:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not alive"
        )
    
    import time
    uptime = time.time() - health_checker.start_time
    
    return LivenessResponse(
        alive=alive,
        uptime_seconds=uptime
    )


@router.get(
    "/metrics", 
    summary="Prometheus Metrics",
    description="Get Prometheus-formatted metrics for monitoring"
)
async def metrics_endpoint():
    """Get Prometheus metrics."""
    metrics_collector = get_metrics_collector()
    metrics_data = metrics_collector.get_prometheus_metrics()
    
    return Response(
        content=metrics_data,
        media_type=PROMETHEUS_CONTENT_TYPE
    )


@router.get(
    "/health/component/{component_name}",
    response_model=ComponentHealth,
    summary="Component Health Check",
    description="Check health of a specific system component"
)
async def component_health_check(component_name: str, force_check: bool = False) -> ComponentHealth:
    """Check health of a specific component."""
    health_checker = get_health_checker()
    
    if component_name not in health_checker.check_configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component '{component_name}' not found"
        )
    
    component_health = await health_checker.get_component_health(component_name, force_check)
    
    # Set response status based on component health
    if component_health.status == HealthStatus.UNHEALTHY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=component_health.message
        )
    
    return component_health


@router.get(
    "/performance",
    summary="Performance Summary",
    description="Get performance metrics and statistics"
)
async def performance_summary():
    """Get system performance summary."""
    metrics_collector = get_metrics_collector()
    return metrics_collector.get_performance_summary()
