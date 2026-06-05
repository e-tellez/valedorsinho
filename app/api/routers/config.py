"""Configuration API router — driving adapter.

Serves Adyen client-side configuration to the frontend.
"""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_auth_service, get_current_user
from app.domain.models.auth import UserProfile
from app.use_cases.auth_service import AuthService

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/client")
def get_client_config(
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    """Return client-side Adyen configuration for the authenticated user.

    The frontend calls this once after sign-in to initialise the Adyen Web SDK.
    """
    credentials = auth_service.resolve_credentials(current_user)
    return {
        "clientKey": credentials.client_key,
        "environment": credentials.environment,
        "merchantAccount": credentials.merchant_account,
    }
