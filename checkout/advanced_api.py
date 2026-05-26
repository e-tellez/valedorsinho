"""Advanced-flow API endpoints.

The Advanced integration uses separate server calls for /paymentMethods,
/payments, and /payments/details — giving full control over each step of
the payment lifecycle.
"""

import logging

from flask import Blueprint, Response, request, jsonify, session, redirect, url_for
import Adyen

from checkout.config import adyen_client, MERCHANT_ACCOUNT
from checkout.checkout_helpers import generate_reference
from checkout.adyen_models import (
    Amount,
    BillingAddress,
    PaymentDetailsRequest,
    PaymentMethodsRequest,
    PaymentRequest,
)

logger = logging.getLogger(__name__)

bp = Blueprint("api", __name__)


def _adyen_error_response(error: Adyen.AdyenError) -> tuple[Response, int]:
    """Build a JSON error response from an Adyen SDK exception."""
    logger.error("Adyen API error: %s – %s", type(error).__name__, error)
    status_code = getattr(error, "status_code", 500) or 500
    return jsonify({"error": str(error), "type": type(error).__name__}), status_code


@bp.route("/result/store", methods=["POST"])
def result_store() -> Response:
    """Receive the payment outcome from the browser and store it in the session.

    The JS calls this endpoint instead of redirecting with query params, so the
    final URL stays clean (/result with no query string).
    """
    body = request.get_json()
    # Save everything the result page needs into the session
    session["payment_result"] = {
        "status": body.get("status", "failure"),
        "result_code": body.get("resultCode", "Unknown"),
        "adyen_response": body.get("adyenResponse"),
    }
    return jsonify({"redirect": url_for("pages.result")})


@bp.route("/api/paymentMethods", methods=["GET"])
def payment_methods() -> Response:
    """Retrieve the payment methods available for this merchant.

    The Adyen Drop-in calls this endpoint on load to know which payment
    method icons and forms to display to the shopper.
    """
    country_code = request.args.get("countryCode", "")
    currency = request.args.get("currency", "")

    payment_methods_request = PaymentMethodsRequest(
        merchant_account=MERCHANT_ACCOUNT,
        amount=Amount(
            value=session.get("amount_minor_units", 1000),
            currency=currency if currency and currency != "undefined" else session.get("currency", "MXN"),
        ),
        country_code=country_code if country_code and country_code != "undefined" else session.get("country_code", "MX"),
        shopper_locale=request.args.get("shopperLocale", "en-US"),
        shopper_reference=session.get("shopper_reference", "") or None,
    )

    request_body = payment_methods_request.model_dump(by_alias=True, exclude_none=True)
    try:
        response = adyen_client.checkout.payments_api.payment_methods(request_body)
    except Adyen.AdyenError as error:
        return _adyen_error_response(error)
    return jsonify({"requestBody": request_body, "response": response.message})


@bp.route("/api/payments", methods=["POST"])
def payments() -> Response:
    """Initiate a payment.

    The browser sends the encrypted payment data (stateData.paymentMethod)
    collected by the Adyen Web Component.  We forward it to Adyen along with
    order details and 3DS2 / native 3DS parameters.
    """
    body = request.get_json()
    is_guest = session.get("is_guest", False)
    shopper_reference = session.get("shopper_reference", "") or None

    # Store the order reference in the server-side session so we can match
    # the /payments/details callback to the correct order later
    order_ref = generate_reference()
    session["order_ref"] = order_ref

    # Build the /payments request using the PaymentRequest model
    raw_billing = body.get("billingAddress")
    payment_request = PaymentRequest(
        merchant_account=MERCHANT_ACCOUNT,
        reference=order_ref,
        amount=Amount(
            value=session.get("amount_minor_units") or body.get("amountMinorUnits", 1000),
            currency=session.get("currency", "MXN"),
        ),
        country_code=session.get("country_code", "MX"),
        payment_method=body.get("paymentMethod", {}),
        return_url=request.host_url + "dropin/handleShopperRedirect",
        origin=request.host_url.rstrip("/"),
        shopper_reference=shopper_reference,
        shopper_ip=request.remote_addr,
        shopper_email=body.get("shopperEmail", "shopper@example.com"),
        browser_info=body.get("browserInfo"),
        billing_address=BillingAddress(**raw_billing) if raw_billing else BillingAddress(),
        store_payment_method=body.get("storePaymentMethod", False) if not is_guest else None,
        recurring_processing_model="CardOnFile" if not is_guest else None,
    )

    # Send the payment request to Adyen
    try:
        response = adyen_client.checkout.payments_api.payments(
            payment_request.model_dump(by_alias=True, exclude_none=True)
        )
    except Adyen.AdyenError as error:
        return _adyen_error_response(error)
    response_body = response.message

    # Persist the payment state data returned by Adyen so that subsequent
    # /payments/details calls can reference it
    session["payment_data"] = response_body.get("paymentData")

    return jsonify(response_body)


@bp.route("/api/payments/details", methods=["POST"])
def payments_details() -> Response:
    """Submit additional authentication details after a 3DS2 challenge.

    When the Drop-in completes a native 3DS2 fingerprint or challenge it
    calls this endpoint with the `details` object (and optionally
    `paymentData`) so we can forward them to Adyen to finalise the payment.
    """
    body = request.get_json()

    details_request = PaymentDetailsRequest(
        details=body.get("details", {}),
        payment_data=body.get("paymentData") or session.get("payment_data"),
    )

    try:
        response = adyen_client.checkout.payments_api.payments_details(
            details_request.model_dump(by_alias=True, exclude_none=True)
        )
    except Adyen.AdyenError as error:
        return _adyen_error_response(error)
    return jsonify(response.message)


@bp.route("/dropin/handleShopperRedirect", methods=["GET", "POST"])
def handle_shopper_redirect() -> Response:
    """Handle the redirect back from the issuer ACS page.

    This endpoint is only reached when the issuer does NOT support native
    3DS2 and redirects the shopper to their authentication page instead.
    After authentication the issuer redirects back here with either query
    params (GET) or form params (POST).
    """
    # Collect the redirect result depending on the HTTP method
    if request.method == "GET":
        redirect_result = request.args.get("redirectResult", "")
    else:
        redirect_result = request.form.get("redirectResult", "")

    details_request = PaymentDetailsRequest(
        details={"redirectResult": redirect_result},
        payment_data=session.get("payment_data", ""),
    )

    try:
        response = adyen_client.checkout.payments_api.payments_details(
            details_request.model_dump(by_alias=True, exclude_none=True)
        )
    except Adyen.AdyenError as error:
        logger.error("Redirect handler Adyen error: %s", error)
        session["payment_result"] = {
            "status": "failure",
            "result_code": "Error",
            "adyen_response": None,
        }
        return redirect(url_for("pages.result"))
    result_code = response.message.get("resultCode", "")

    # Store the result in the session so /result can render a clean URL
    status = "success" if result_code in ("Authorised", "Pending", "Received") else "failure"
    session["payment_result"] = {
        "status": status,
        "result_code": result_code,
        "adyen_response": response.message if status == "success" else None,
    }
    return redirect(url_for("pages.result"))
