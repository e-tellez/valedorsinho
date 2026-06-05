"""FastAPI application factory.

Creates the FastAPI app, configures CORS middleware, and registers
all API routers.  Follows hexagonal architecture: routers live in
app.api.routers (driving adapters), use cases in app.use_cases,
port interfaces in app.ports, and driven adapters in app.adapters.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# api.config must be imported first – it loads .env and applies
# the SSL fix before the Adyen client (initialised inside config) makes
# any requests.
from app.api.config import CORS_ORIGINS
from app.api.routers import checkout, terminal_payments, terminal_fleet, tools, config

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

    # Register routers (driving adapters)
    application.include_router(checkout.router)
    application.include_router(terminal_payments.router)
    application.include_router(terminal_fleet.router)
    application.include_router(tools.router)
    application.include_router(config.router)

    @application.get("/health")
    async def health_check() -> dict[str, str]:
        """Simple health check endpoint."""
        return {"status": "ok"}

    @application.get("/goodmorning")
    async def goodmorning() -> dict[str, str]:
        """Wake-up endpoint.

        Called by the frontend when a user on an Adyen domain loads the app,
        ensuring the server is active after a period of inactivity.
        """
        return {"status": "awake"}

    return application


app = create_app()
