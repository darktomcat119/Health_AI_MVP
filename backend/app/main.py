"""FastAPI application factory with lifespan management.

Creates and configures the FastAPI application with:
- CORS middleware for frontend communication
- Exception handlers for custom exceptions
- API router mounting with versioned prefix
- Structured logging initialization
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.exceptions import (
    ChatbotBaseException,
    InvalidMessageException,
    SessionExpiredException,
    SessionNotFoundException,
)
from app.routers import chat, health
from app.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        None during the application lifetime.
    """
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info(
        "Starting %s v%s in %s mode",
        settings.app_name,
        settings.app_version,
        settings.app_env,
    )
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered clinical chatbot for mental health support",
        lifespan=lifespan,
    )

    _configure_cors(application, settings)
    _register_exception_handlers(application)
    _include_routers(application)

    return application


def _configure_cors(application: FastAPI, settings) -> None:
    """Add CORS middleware for frontend communication.

    Args:
        application: FastAPI app to configure.
        settings: Application settings with frontend URL.
    """
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _register_exception_handlers(application: FastAPI) -> None:
    """Register custom exception handlers for structured error responses.

    Args:
        application: FastAPI app to register handlers on.
    """

    @application.exception_handler(SessionNotFoundException)
    async def session_not_found_handler(
        request: Request, exc: SessionNotFoundException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": exc.message, "error_code": "SESSION_NOT_FOUND"},
        )

    @application.exception_handler(SessionExpiredException)
    async def session_expired_handler(
        request: Request, exc: SessionExpiredException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=410,
            content={"detail": exc.message, "error_code": "SESSION_EXPIRED"},
        )

    @application.exception_handler(InvalidMessageException)
    async def invalid_message_handler(
        request: Request, exc: InvalidMessageException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message, "error_code": "INVALID_MESSAGE"},
        )

    @application.exception_handler(ChatbotBaseException)
    async def chatbot_base_handler(
        request: Request, exc: ChatbotBaseException,
    ) -> JSONResponse:
        logger.error("Unhandled chatbot exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred", "error_code": "INTERNAL_ERROR"},
        )


def _include_routers(application: FastAPI) -> None:
    """Mount API routers with versioned prefix.

    Args:
        application: FastAPI app to mount routers on.
    """
    application.include_router(health.router, prefix="/api/v1")
    application.include_router(chat.router, prefix="/api/v1")


app = create_app()
