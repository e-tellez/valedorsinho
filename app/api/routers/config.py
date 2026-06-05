"""Configuration API router — driving adapter.

Serves Adyen client-side configuration to the frontend.
"""

from fastapi import APIRouter

from app.api.config import CLIENT_KEY, ADYEN_ENVIRONMENT, MERCHANT_ACCOUNT

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/client")
async def get_client_config() -> dict[str, str]:
    """Return client-side Adyen configuration.

    The frontend calls this once on startup to get the values needed
    to initialise the Adyen Web SDK (AdyenCheckout).
    """
    return {
        "clientKey": CLIENT_KEY,
        "environment": ADYEN_ENVIRONMENT,
        "merchantAccount": MERCHANT_ACCOUNT,
    }
