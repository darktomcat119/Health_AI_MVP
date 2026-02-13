"""Health check endpoint.

Provides service status information for monitoring and load balancers.
"""

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.dependencies import get_session_service
from app.models.schemas import HealthResponse
from app.services.session_service import SessionService

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns service status, version, and active session count.",
)
def health_check(
    session_service: SessionService = Depends(get_session_service),
) -> HealthResponse:
    """Return current service health status.

    Args:
        session_service: Injected session service for active session count.

    Returns:
        HealthResponse with service status information.
    """
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        active_sessions=session_service.count_active(),
    )
