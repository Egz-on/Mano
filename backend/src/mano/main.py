"""Main FastAPI application."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mano.dependencies import setup_rate_limiting

from .domain.exceptions.base import DomainError
from .infrastructure.cache.connection import redis_client
from .infrastructure.config.settings import get_settings
from .infrastructure.database.connection import database
from .presentation.api.chat_ws import router as chat_ws_router
from .presentation.api.v1.auth_route import router as auth_router
from .presentation.api.v1.availability_route import router as availability_router
from .presentation.api.v1.category_route import router as categories_router
from .presentation.api.v1.chat_route import router as chat_router
from .presentation.api.v1.job_route import router as jobs_router
from .presentation.api.v1.review_route import router as reviews_router
from .presentation.api.v1.service_image import router as service_images_router
from .presentation.api.v1.service_route import router as services_router
from .presentation.api.v1.user_route import router as users_router
from .presentation.websockets.chat import chat_redis_bridge

settings = get_settings()
log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.api.title,
        description=settings.api.description,
        version=settings.api.version,
        docs_url=settings.api.docs_url,
        redoc_url=settings.api.redoc_url,
        debug=settings.debug,
        lifespan=lifespan,
    )
    setup_rate_limiting(app)

    origins = ["*"] if settings.is_development else []
    origins.append("http://localhost")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(service_images_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(services_router, prefix="/api/v1")
    app.include_router(categories_router, prefix="/api/v1")
    app.include_router(availability_router, prefix="/api/v1")
    app.include_router(reviews_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(jobs_router, prefix="/api/v1")
    app.include_router(chat_ws_router)

    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.is_production else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        wrapper_class=structlog.stdlib.BoundLogger,
    )
    logging.getLogger().setLevel(log_level)

    @app.exception_handler(DomainError)
    async def domain_exception_handler(request: Request, exc: DomainError) -> JSONResponse:
        logger = structlog.get_logger()
        logger.warning("Domain error", error=str(exc), path=str(request.url))
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(exc)})

    @app.get("/health", summary="Health check", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "service": "Mano"}

    return app


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan hooks."""
    _ = app
    logger = structlog.get_logger()
    logger.info("Starting Mano API", environment=settings.environment)
    try:
        redis = await redis_client.get_client()
        logger.info("Redis cache connected")
        await chat_redis_bridge.start(redis)
    except Exception as exc:  # pragma: no cover - optional infrastructure
        logger.warning("Redis cache unavailable", error=str(exc))

    yield

    logger.info("Shutting down Mano API")
    await chat_redis_bridge.stop()
    await database.close()
    await redis_client.close()
    logger.info("Redis cache disconnected")


app = create_app()
