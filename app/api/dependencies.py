"""FastAPI dependency injection wiring.

Composes adapters into use cases and exposes them as FastAPI ``Depends`` callables.
"""

from functools import lru_cache

import Adyen
from fastapi import Depends, HTTPException, Request

from app.adapters.checkout_adapter import CheckoutAdapter
from app.adapters.management_adapter import ManagementAdapter
from app.adapters.supabase_adapter import SupabaseAdapter
from app.adapters.terminal_adapter import TerminalAdapter
from app.adapters.terminal_decoder import decode_additional_response, extract_payment_summary
from app.adapters.validator_adapter import ValidatorAdapter
from app.adapters.webhook_adapter import WebhookAdapter
from app.api.config import (
    ADYEN_API_KEY,
    ADYEN_ENVIRONMENT,
    CLIENT_KEY,
    MERCHANT_ACCOUNT,
    SUPABASE_JWT_SECRET,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
)
from app.domain.models.auth import AdyenCredentials, UserProfile
from app.domain.verticals import VERTICALS
from app.use_cases.auth_service import AuthService
from app.use_cases.checkout_service import CheckoutService
from app.use_cases.terminal_fleet_service import TerminalFleetService
from app.use_cases.terminal_payment_service import TerminalPaymentService
from app.use_cases.tools_service import ToolsService
from app.use_cases.webhook_service import WebhookService


# ---------------------------------------------------------------------------
# Singletons (stateless, config-based)
# ---------------------------------------------------------------------------

@lru_cache
def _default_credentials() -> AdyenCredentials:
    return AdyenCredentials(
        api_key=ADYEN_API_KEY,
        client_key=CLIENT_KEY,
        merchant_account=MERCHANT_ACCOUNT,
        environment=ADYEN_ENVIRONMENT,
    )


@lru_cache
def _supabase_adapter() -> SupabaseAdapter:
    return SupabaseAdapter(
        supabase_url=SUPABASE_URL,
        service_role_key=SUPABASE_SERVICE_ROLE_KEY,
        jwt_secret=SUPABASE_JWT_SECRET,
        environment=ADYEN_ENVIRONMENT,
    )


@lru_cache
def _validator_adapter() -> ValidatorAdapter:
    return ValidatorAdapter()


# ---------------------------------------------------------------------------
# Auth service and current-user resolution
# ---------------------------------------------------------------------------

def get_auth_service() -> AuthService:
    return AuthService(
        auth_gateway=_supabase_adapter(),
        default_credentials=_default_credentials(),
    )


def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserProfile:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth_header[7:]
    try:
        return auth_service.verify_token(token)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))


# ---------------------------------------------------------------------------
# Helper: build a per-request Adyen client from resolved credentials
# ---------------------------------------------------------------------------

def _build_adyen_client(credentials: AdyenCredentials) -> Adyen.Adyen:
    return Adyen.Adyen(
        xapikey=credentials.api_key,
        platform=credentials.environment,
        merchant_account=credentials.merchant_account,
    )


# ---------------------------------------------------------------------------
# Application services exposed to routers via Depends()
# ---------------------------------------------------------------------------

def get_checkout_service(
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> CheckoutService:
    credentials = auth_service.resolve_credentials(current_user)
    return CheckoutService(
        gateway=CheckoutAdapter(_build_adyen_client(credentials)),
        merchant_account=credentials.merchant_account,
    )


def get_terminal_payment_service(
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> TerminalPaymentService:
    credentials = auth_service.resolve_credentials(current_user)
    return TerminalPaymentService(
        terminal_gateway=TerminalAdapter(
            api_key=credentials.api_key,
            environment=credentials.environment,
        ),
        management_gateway=ManagementAdapter(_build_adyen_client(credentials)),
        decode_additional_response_fn=decode_additional_response,
        extract_payment_summary_fn=extract_payment_summary,
    )


def get_terminal_fleet_service(
    current_user: UserProfile = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> TerminalFleetService:
    credentials = auth_service.resolve_credentials(current_user)
    return TerminalFleetService(
        management_gateway=ManagementAdapter(_build_adyen_client(credentials)),
    )


def get_tools_service() -> ToolsService:
    return ToolsService(
        validator=_validator_adapter(),
        verticals=VERTICALS,
    )


@lru_cache
def _webhook_adapter() -> WebhookAdapter:
    return WebhookAdapter(
        supabase_url=SUPABASE_URL,
        service_role_key=SUPABASE_SERVICE_ROLE_KEY,
    )


def get_webhook_service() -> WebhookService:
    return WebhookService(gateway=_webhook_adapter())
