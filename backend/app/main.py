"""FastAPI application factory.

Creates the FastAPI app, configures CORS middleware, and registers
all API routers.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# config must be imported first – it loads .env and applies the SSL fix
# before the Adyen client (initialised inside config) makes any requests.
from app.core.config import CORS_ORIGINS
from app.routers import checkout, terminal_payments, terminal_fleet, tools, config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Application factory.

    Creates and configures the FastAPI app with CORS middleware and
    all API routers registered.
    """
    application = FastAPI(
        title="Valedorsinho API",
        description="Backend API for Adyen integration demos",
        version="1.0.0",
    )

    # CORS – allow the Next.js frontend to call the API
    application.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    application.include_router(checkout.router)
    application.include_router(terminal_payments.router)
    application.include_router(terminal_fleet.router)
    application.include_router(tools.router)
    application.include_router(config.router)

    @application.get("/health")
    async def health_check() -> dict[str, str]:
        """Simple health check endpoint."""
        return {"status": "ok"}

    return application


app = create_app()
