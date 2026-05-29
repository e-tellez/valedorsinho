"""Configuration API endpoint.

Serves the Adyen client-side configuration (client key, environment)
to the frontend so it can initialise the Adyen Web SDK without needing
NEXT_PUBLIC_ environment variables.
"""

from fastapi import APIRouter

from app.core.config import CLIENT_KEY, ADYEN_ENVIRONMENT, MERCHANT_ACCOUNT

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/client")
async def get_client_config() -> dict[str, str | None]:
    """Return client-side Adyen configuration.

    The frontend calls this once on startup to get the values needed
    to initialise the Adyen Web SDK (AdyenCheckout).
    """
    return {
        "clientKey": CLIENT_KEY,
        "environment": ADYEN_ENVIRONMENT,
        "merchantAccount": MERCHANT_ACCOUNT,
    }
