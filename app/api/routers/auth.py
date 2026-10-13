"""Auth router — credential settings endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_auth_service, get_current_user
from app.api.schemas.accounts import (
    AccountListResponse,
    AdyenAccountResponse,
    CreateAccountBody,
    UpdateAccountBody,
)
from app.api.schemas.auth import AdyenConfigResponse, UpsertAdyenConfigBody
from app.domain.models.auth import AdyenAccount, UserProfile, UserRole
from app.use_cases.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _account_to_response(account: AdyenAccount) -> AdyenAccountResponse:
    return AdyenAccountResponse(
        id=account.id,
        label=account.label,
        client_key=account.client_key,
        merchant_account=account.merchant_account,
        is_active=account.is_active,
        locked=account.locked,
        api_key_configured=account.api_key_configured,
    )


@router.get("/config", response_model=AdyenConfigResponse)
def get_config(
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdyenConfigResponse:
    """Return the active Adyen credentials for the authenticated user."""
    personal_credentials = auth_service.get_user_config(current_user)
    credentials = personal_credentials or auth_service.resolve_credentials(current_user)
    return AdyenConfigResponse(
        role=current_user.role,
        client_key=credentials.client_key,
        merchant_account=credentials.merchant_account,
        environment=credentials.environment,
        is_custom=personal_credentials is not None,
        locked=personal_credentials.locked if personal_credentials else False,
        api_key_configured=personal_credentials is not None and bool(personal_credentials.api_key),
        can_configure=(
            current_user.role in (UserRole.ADMIN, UserRole.IM)
            and not (personal_credentials and personal_credentials.locked)
        ),
    )


@router.put("/config", response_model=AdyenConfigResponse)
def update_config(
    body: UpsertAdyenConfigBody,
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdyenConfigResponse:
    """Save personal Adyen credentials. Allowed for admin and im roles only."""
    try:
        saved_credentials = auth_service.update_user_config(
            user=current_user,
            api_key=body.api_key,
            client_key=body.client_key,
            merchant_account=body.merchant_account,
        )
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return AdyenConfigResponse(
        role=current_user.role,
        client_key=saved_credentials.client_key,
        merchant_account=saved_credentials.merchant_account,
        environment=saved_credentials.environment,
        is_custom=True,
        locked=saved_credentials.locked,
        api_key_configured=True,
        can_configure=True,
    )


# ---------------------------------------------------------------------------
# Multiple saved company accounts (admin / im only)
# ---------------------------------------------------------------------------


@router.get("/accounts", response_model=AccountListResponse)
def list_accounts(
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AccountListResponse:
    """List the user's saved company accounts. Admin and im roles only."""
    try:
        accounts = auth_service.list_accounts(current_user)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    return AccountListResponse(accounts=[_account_to_response(a) for a in accounts])


@router.post("/accounts", response_model=AdyenAccountResponse)
def create_account(
    body: CreateAccountBody,
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdyenAccountResponse:
    """Create a new saved company account. The first account becomes active."""
    try:
        account = auth_service.create_account(
            user=current_user,
            label=body.label,
            api_key=body.api_key,
            client_key=body.client_key,
            merchant_account=body.merchant_account,
        )
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return _account_to_response(account)


@router.put("/accounts/{config_id}", response_model=AdyenAccountResponse)
def update_account(
    config_id: str,
    body: UpdateAccountBody,
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdyenAccountResponse:
    """Update a saved company account. A blank API key preserves the stored one."""
    try:
        account = auth_service.update_account(
            user=current_user,
            config_id=config_id,
            label=body.label,
            api_key=body.api_key,
            client_key=body.client_key,
            merchant_account=body.merchant_account,
        )
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except KeyError:
        raise HTTPException(status_code=404, detail="Account not found")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return _account_to_response(account)


@router.delete("/accounts/{config_id}", status_code=204)
def delete_account(
    config_id: str,
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    """Delete a saved company account. Locked accounts cannot be deleted."""
    try:
        auth_service.delete_account(current_user, config_id)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except KeyError:
        raise HTTPException(status_code=404, detail="Account not found")


@router.put("/accounts/{config_id}/activate", response_model=AdyenAccountResponse)
def activate_account(
    config_id: str,
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdyenAccountResponse:
    """Make the given account the active one for the current user."""
    try:
        account = auth_service.activate_account(current_user, config_id)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except KeyError:
        raise HTTPException(status_code=404, detail="Account not found")
    return _account_to_response(account)
