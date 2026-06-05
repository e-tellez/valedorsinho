"""FastAPI dependency injection wiring.

Composes adapters into use cases and exposes them as FastAPI ``Depends`` callables.
"""

from functools import lru_cache

from app.use_cases.checkout_service import CheckoutService
from app.use_cases.terminal_fleet_service import TerminalFleetService
from app.use_cases.terminal_payment_service import TerminalPaymentService
from app.use_cases.tools_service import ToolsService
from app.adapters.checkout_adapter import CheckoutAdapter
from app.adapters.management_adapter import ManagementAdapter
from app.adapters.terminal_adapter import TerminalAdapter
from app.adapters.validator_adapter import ValidatorAdapter
from app.api.config import (
    ADYEN_API_KEY,
    ADYEN_ENVIRONMENT,
    MERCHANT_ACCOUNT,
    adyen_client,
)
from app.domain.verticals import VERTICALS
from app.adapters.terminal_decoder import (
    decode_additional_response,
    extract_payment_summary,
)


# ---------------------------------------------------------------------------
# Singleton adapters (created once)
# ---------------------------------------------------------------------------

@lru_cache
def _checkout_adapter() -> CheckoutAdapter:
    return CheckoutAdapter(adyen_client)


@lru_cache
def _management_adapter() -> ManagementAdapter:
    return ManagementAdapter(adyen_client)


@lru_cache
def _terminal_adapter() -> TerminalAdapter:
    return TerminalAdapter(api_key=ADYEN_API_KEY, environment=ADYEN_ENVIRONMENT)


@lru_cache
def _validator_adapter() -> ValidatorAdapter:
    return ValidatorAdapter()


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
