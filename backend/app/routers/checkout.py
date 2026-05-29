"""Checkout API endpoints.

Combines the Advanced flow (/paymentMethods, /payments, /payments/details)
and the Sessions flow (/sessions) into a single router.  All Adyen API
calls stay server-side; the Next.js frontend sends lightweight JSON
requests and receives the Adyen response back.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
import Adyen

from app.core.config import adyen_client, MERCHANT_ACCOUNT
from app.core.helpers import generate_reference
from app.models.checkout import (
    Amount,
    BillingAddress,
    CreatePaymentBody,
    CreateSessionBody,
    DisableStoredMethodBody,
    PaymentDetailsBody,
    PaymentDetailsRequest,
    PaymentMethodsRequest,
    PaymentRequest,
    RedirectBody,
    SessionsRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/checkout", tags=["checkout"])


def _adyen_error_response(error: Adyen.AdyenError) -> None:
    """Raise an HTTPException from an Adyen SDK exception."""
    logger.error("Adyen API error: %s – %s", type(error).__name__, error)
    status_code = getattr(error, "status_code", 500) or 500
    raise HTTPException(status_code=status_code, detail=str(error))


# ---------------------------------------------------------------------------
# GET /api/checkout/payment-methods
# ---------------------------------------------------------------------------

@router.get("/payment-methods")
async def payment_methods(
    amount_value: int = Query(default=1000, alias="amountValue"),
    currency: str = Query(default="MXN"),
    country_code: str = Query(default="MX", alias="countryCode"),
    shopper_locale: str = Query(default="en-US", alias="shopperLocale"),
    shopper_reference: str | None = Query(default=None, alias="shopperReference"),
) -> dict[str, Any]:
    """Retrieve the payment methods available for this merchant."""
    payment_methods_request = PaymentMethodsRequest(
        merchant_account=MERCHANT_ACCOUNT,
        amount=Amount(value=amount_value, currency=currency),
        country_code=country_code,
        shopper_locale=shopper_locale,
        shopper_reference=shopper_reference,
    )

    request_body = payment_methods_request.model_dump(by_alias=True, exclude_none=True)
    try:
        response = adyen_client.checkout.payments_api.payment_methods(request_body)
    except Adyen.AdyenError as error:
        _adyen_error_response(error)
    return {"requestBody": request_body, "response": response.message}


# ---------------------------------------------------------------------------
# POST /api/checkout/payments
# ---------------------------------------------------------------------------

@router.post("/payments")
async def payments(body: CreatePaymentBody, request: Request) -> dict[str, Any]:
    """Initiate a payment.

    The frontend sends the encrypted payment data collected by the Adyen
    Web Component along with order details.  We forward it to Adyen.
    """
    order_ref = generate_reference()

    raw_billing = body.billing_address
    payment_request = PaymentRequest(
        merchant_account=MERCHANT_ACCOUNT,
        reference=order_ref,
        amount=Amount(value=body.amount_value, currency=body.currency),
        country_code=body.country_code,
        payment_method=body.payment_method,
        return_url=body.return_url,
        origin=body.origin,
        shopper_reference=body.shopper_reference,
        shopper_ip=request.client.host if request.client else "127.0.0.1",
        shopper_email=body.shopper_email,
        browser_info=body.browser_info,
        billing_address=BillingAddress(**raw_billing) if raw_billing else BillingAddress(),
        store_payment_method=body.store_payment_method if not body.is_guest else None,
        recurring_processing_model="CardOnFile" if not body.is_guest and body.shopper_reference else None,
    )

    try:
        response = adyen_client.checkout.payments_api.payments(
            payment_request.model_dump(by_alias=True, exclude_none=True)
        )
    except Adyen.AdyenError as error:
        _adyen_error_response(error)

    return response.message


# ---------------------------------------------------------------------------
# POST /api/checkout/payments/details
# ---------------------------------------------------------------------------

@router.post("/payments/details")
async def payments_details(body: PaymentDetailsBody) -> dict[str, Any]:
    """Submit additional authentication details after a 3DS2 challenge."""
    details_request = PaymentDetailsRequest(
        details=body.details,
        payment_data=body.payment_data,
    )

    try:
        response = adyen_client.checkout.payments_api.payments_details(
            details_request.model_dump(by_alias=True, exclude_none=True)
        )
    except Adyen.AdyenError as error:
        _adyen_error_response(error)
    return response.message


# ---------------------------------------------------------------------------
# POST /api/checkout/sessions
# ---------------------------------------------------------------------------

@router.post("/sessions")
async def sessions(body: CreateSessionBody) -> dict[str, Any]:
    """Create an Adyen session for the Sessions integration flow."""
    order_ref = generate_reference()

    sessions_request = SessionsRequest(
        merchant_account=MERCHANT_ACCOUNT,
        reference=order_ref,
        amount=Amount(value=body.amount_value, currency=body.currency),
        country_code=body.country_code,
        return_url=body.return_url,
        shopper_reference=body.shopper_reference,
        shopper_email=body.shopper_email,
        store_payment_method_mode=(
            "askForConsent"
            if not body.is_guest and body.shopper_reference
            else None
        ),
        recurring_processing_model=(
            "CardOnFile"
            if not body.is_guest and body.shopper_reference
            else None
        ),
    )

    request_body = sessions_request.model_dump(by_alias=True, exclude_none=True)
    try:
        response = adyen_client.checkout.payments_api.sessions(request_body)
    except Adyen.AdyenError as error:
        _adyen_error_response(error)

    return {"requestBody": request_body, "response": response.message}


# ---------------------------------------------------------------------------
# POST /api/checkout/disable
# ---------------------------------------------------------------------------

@router.post("/disable")
async def disable_stored_payment_method(body: DisableStoredMethodBody) -> dict[str, Any]:
    """Remove a stored (tokenised) payment method."""
    disable_request = {
        "merchantAccount": MERCHANT_ACCOUNT,
        "shopperReference": body.shopper_reference,
        "recurringDetailReference": body.stored_payment_method_id,
    }

    try:
        response = adyen_client.recurring.disable(disable_request)
    except Adyen.AdyenError as error:
        _adyen_error_response(error)

    return response.message


# ---------------------------------------------------------------------------
# POST /api/checkout/redirect
# ---------------------------------------------------------------------------

@router.post("/redirect")
async def handle_redirect(body: RedirectBody) -> dict[str, Any]:
    """Handle the redirect back from the issuer ACS page.

    The frontend reads `redirectResult` from the URL after the issuer
    redirects back, then calls this endpoint with the redirect result
    and the stored paymentData so we can finalise the payment.
    """
    details_request = PaymentDetailsRequest(
        details={"redirectResult": body.redirect_result},
        payment_data=body.payment_data,
    )

    try:
        response = adyen_client.checkout.payments_api.payments_details(
            details_request.model_dump(by_alias=True, exclude_none=True)
        )
    except Adyen.AdyenError as error:
        logger.error("Redirect handler Adyen error: %s", error)
        _adyen_error_response(error)

    return response.message
