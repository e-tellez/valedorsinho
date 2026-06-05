"""Checkout API router — driving adapter.

Thin HTTP layer that validates incoming requests, delegates to
CheckoutService, and returns responses.
"""

import logging
from typing import Any

import Adyen
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.dependencies import get_checkout_service
from app.api.schemas.checkout import (
    CreatePaymentBody,
    CreateSessionBody,
    DisableStoredMethodBody,
    PaymentDetailsBody,
    RedirectBody,
)
from app.application.checkout_service import CheckoutService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/checkout", tags=["checkout"])


def _handle_adyen_error(error: Adyen.AdyenError) -> None:
    logger.error("Adyen API error: %s – %s", type(error).__name__, error)
    status_code = getattr(error, "status_code", 500) or 500
    raise HTTPException(status_code=status_code, detail=str(error))


# ---------------------------------------------------------------------------
# GET /api/checkout/payment-methods
# ---------------------------------------------------------------------------

@router.get("/payment-methods")
async def payment_methods(
    service: CheckoutService = Depends(get_checkout_service),
    amount_value: int = Query(default=1000, alias="amountValue"),
    currency: str = Query(default="MXN"),
    country_code: str = Query(default="MX", alias="countryCode"),
    shopper_locale: str = Query(default="en-US", alias="shopperLocale"),
    shopper_reference: str | None = Query(default=None, alias="shopperReference"),
) -> dict[str, Any]:
    """Retrieve the payment methods available for this merchant."""
    try:
        return service.get_payment_methods(
            amount_value=amount_value,
            currency=currency,
            country_code=country_code,
            shopper_locale=shopper_locale,
            shopper_reference=shopper_reference,
        )
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)


# ---------------------------------------------------------------------------
# POST /api/checkout/payments
# ---------------------------------------------------------------------------

@router.post("/payments")
async def payments(
    body: CreatePaymentBody,
    request: Request,
    service: CheckoutService = Depends(get_checkout_service),
) -> dict[str, Any]:
    """Initiate a payment."""
    try:
        return service.create_payment(
            payment_method=body.payment_method,
            amount_value=body.amount_value,
            currency=body.currency,
            country_code=body.country_code,
            return_url=body.return_url,
            origin=body.origin,
            shopper_ip=request.client.host if request.client else "127.0.0.1",
            shopper_reference=body.shopper_reference,
            is_guest=body.is_guest,
            shopper_email=body.shopper_email,
            browser_info=body.browser_info,
            billing_address=body.billing_address,
            store_payment_method=body.store_payment_method,
        )
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)


# ---------------------------------------------------------------------------
# POST /api/checkout/payments/details
# ---------------------------------------------------------------------------

@router.post("/payments/details")
async def payments_details(
    body: PaymentDetailsBody,
    service: CheckoutService = Depends(get_checkout_service),
) -> dict[str, Any]:
    """Submit additional authentication details after a 3DS2 challenge."""
    try:
        return service.submit_payment_details(
            details=body.details,
            payment_data=body.payment_data,
        )
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)


# ---------------------------------------------------------------------------
# POST /api/checkout/sessions
# ---------------------------------------------------------------------------

@router.post("/sessions")
async def sessions(
    body: CreateSessionBody,
    service: CheckoutService = Depends(get_checkout_service),
) -> dict[str, Any]:
    """Create an Adyen session for the Sessions integration flow."""
    try:
        return service.create_session(
            amount_value=body.amount_value,
            currency=body.currency,
            country_code=body.country_code,
            return_url=body.return_url,
            shopper_reference=body.shopper_reference,
            is_guest=body.is_guest,
            shopper_email=body.shopper_email,
        )
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)


# ---------------------------------------------------------------------------
# POST /api/checkout/disable
# ---------------------------------------------------------------------------

@router.post("/disable")
async def disable_stored_payment_method(
    body: DisableStoredMethodBody,
    service: CheckoutService = Depends(get_checkout_service),
) -> dict[str, Any]:
    """Remove a stored (tokenised) payment method."""
    try:
        return service.disable_stored_method(
            shopper_reference=body.shopper_reference,
            stored_payment_method_id=body.stored_payment_method_id,
        )
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)


# ---------------------------------------------------------------------------
# POST /api/checkout/redirect
# ---------------------------------------------------------------------------

@router.post("/redirect")
async def handle_redirect(
    body: RedirectBody,
    service: CheckoutService = Depends(get_checkout_service),
) -> dict[str, Any]:
    """Handle the redirect back from the issuer ACS page."""
    try:
        return service.handle_redirect(
            redirect_result=body.redirect_result,
            payment_data=body.payment_data,
        )
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)
