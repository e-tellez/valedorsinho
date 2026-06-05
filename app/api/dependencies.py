"""FastAPI dependency injection wiring.

Composes infrastructure adapters into application services and exposes
them as FastAPI ``Depends`` callables.
"""

from functools import lru_cache

from app.application.checkout_service import CheckoutService
from app.application.terminal_fleet_service import TerminalFleetService
from app.application.terminal_payment_service import TerminalPaymentService
from app.application.tools_service import ToolsService
from app.infrastructure.adyen_checkout_adapter import AdyenCheckoutAdapter
from app.infrastructure.adyen_management_adapter import AdyenManagementAdapter
from app.infrastructure.adyen_terminal_adapter import AdyenTerminalAdapter
from app.infrastructure.adyen_validator_adapter import AdyenValidatorAdapter
from app.infrastructure.config import (
    ADYEN_API_KEY,
    ADYEN_ENVIRONMENT,
    MERCHANT_ACCOUNT,
    adyen_client,
)
from app.infrastructure.data.verticals import VERTICALS
from app.infrastructure.terminal_decoder import (
    decode_additional_response,
    extract_payment_summary,
)


# ---------------------------------------------------------------------------
# Singleton adapters (created once)
# ---------------------------------------------------------------------------

@lru_cache
def _checkout_adapter() -> AdyenCheckoutAdapter:
    return AdyenCheckoutAdapter(adyen_client)


@lru_cache
def _management_adapter() -> AdyenManagementAdapter:
    return AdyenManagementAdapter(adyen_client)


@lru_cache
def _terminal_adapter() -> AdyenTerminalAdapter:
    return AdyenTerminalAdapter(api_key=ADYEN_API_KEY, environment=ADYEN_ENVIRONMENT)


@lru_cache
def _validator_adapter() -> AdyenValidatorAdapter:
    return AdyenValidatorAdapter()


# ---------------------------------------------------------------------------
# Application services exposed to routers via Depends()
# ---------------------------------------------------------------------------

def get_checkout_service() -> CheckoutService:
    return CheckoutService(
        gateway=_checkout_adapter(),
        merchant_account=MERCHANT_ACCOUNT,
    )


def get_terminal_payment_service() -> TerminalPaymentService:
    return TerminalPaymentService(
        terminal_gateway=_terminal_adapter(),
        management_gateway=_management_adapter(),
        decode_additional_response_fn=decode_additional_response,
        extract_payment_summary_fn=extract_payment_summary,
    )


def get_terminal_fleet_service() -> TerminalFleetService:
    return TerminalFleetService(
        management_gateway=_management_adapter(),
    )


def get_tools_service() -> ToolsService:
    return ToolsService(
        validator=_validator_adapter(),
        verticals=VERTICALS,
    )
