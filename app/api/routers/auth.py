"""Auth router — credential settings endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.config import ADYEN_ENVIRONMENT
from app.api.dependencies import get_auth_service, get_current_user
from app.api.schemas.auth import AdyenConfigResponse, UpsertAdyenConfigBody
from app.domain.models.auth import AdyenCredentials, UserProfile, UserRole
from app.use_cases.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/config", response_model=AdyenConfigResponse)
def get_config(
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdyenConfigResponse:
    """Return the active Adyen credentials for the authenticated user."""
    credentials = auth_service.resolve_credentials(current_user)
    return AdyenConfigResponse(
        role=current_user.role,
        client_key=credentials.client_key,
        merchant_account=credentials.merchant_account,
        environment=credentials.environment,
        is_custom=current_user.role in (UserRole.ADMIN, UserRole.IM),
        locked=credentials.locked,
    )


@router.put("/config", response_model=AdyenConfigResponse)
def update_config(
    body: UpsertAdyenConfigBody,
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdyenConfigResponse:
    """Save personal Adyen credentials. Allowed for admin and im roles only."""
    try:
        saved_credentials = auth_service.save_user_config(
            user=current_user,
            credentials=AdyenCredentials(
                api_key=body.api_key,
                client_key=body.client_key,
                merchant_account=body.merchant_account,
                environment=ADYEN_ENVIRONMENT,
            ),
        )
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    return AdyenConfigResponse(
        role=current_user.role,
        client_key=saved_credentials.client_key,
        merchant_account=saved_credentials.merchant_account,
        environment=saved_credentials.environment,
        is_custom=True,
        locked=saved_credentials.locked,
    )
