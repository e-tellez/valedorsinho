"""Configuration API router — driving adapter.

Serves Adyen client-side configuration to the frontend.
"""

from fastapi import APIRouter, Depends, HTTPException

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
    Returns 404 when no usable Adyen configuration is available (blank client
    key or merchant account) so the frontend does not initialise the SDK with
    empty values. The API key is never inspected or returned here.
    """
    credentials = auth_service.resolve_credentials(current_user)
    if not credentials.client_key.strip() or not credentials.merchant_account.strip():
        raise HTTPException(
            status_code=404,
            detail="No Adyen configuration found. Please complete the setup step first.",
        )
    return {
        "clientKey": credentials.client_key,
        "environment": credentials.environment,
        "merchantAccount": credentials.merchant_account,
    }
