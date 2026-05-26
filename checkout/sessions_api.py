"""Sessions-flow API endpoints.

The /sessions integration creates a single Adyen session and lets the
Web SDK handle the full payment lifecycle (payment methods, payments, 3DS)
on the client side — no further server calls required beyond this file.
"""

import logging

from flask import Blueprint, Response, render_template, request, jsonify, session
import Adyen

from checkout.config import adyen_client, MERCHANT_ACCOUNT
from checkout.helpers import generate_reference
from checkout.models import Amount, SessionsRequest

logger = logging.getLogger(__name__)

bp = Blueprint("sessions_api", __name__)


def _adyen_error_response(error: Adyen.AdyenError) -> tuple[Response, int]:
    """Build a JSON error response from an Adyen SDK exception."""
    logger.error("Adyen API error: %s – %s", type(error).__name__, error)
    status_code = getattr(error, "status_code", 500) or 500
    return jsonify({"error": str(error), "type": type(error).__name__}), status_code


@bp.route("/api/sessions", methods=["POST"])
def sessions() -> Response:
    """Create an Adyen session.

    The /sessions endpoint creates a payment session that the Adyen Web SDK
    uses to handle the full payment lifecycle on the client side — including
    payment methods, payments, and 3DS — without further server calls.
    """
    is_guest = session.get("is_guest", False)
    shopper_reference = session.get("shopper_reference", "") or None
    order_ref = generate_reference()
    session["order_ref"] = order_ref

    sessions_request = SessionsRequest(
        merchant_account=MERCHANT_ACCOUNT,
        reference=order_ref,
        amount=Amount(
            value=session.get("amount_minor_units", 1000),
            currency=session.get("currency", "MXN"),
        ),
        country_code=session.get("country_code", "MX"),
        return_url=request.host_url.rstrip("/") + "/sessions/handleShopperRedirect",
        shopper_reference=shopper_reference,
        shopper_email="shopper@example.com",
        store_payment_method_mode="askForConsent" if not is_guest and shopper_reference else None,
        recurring_processing_model="CardOnFile" if not is_guest and shopper_reference else None,
    )

    request_body = sessions_request.model_dump(by_alias=True, exclude_none=True)
    try:
        response = adyen_client.checkout.payments_api.sessions(request_body)
    except Adyen.AdyenError as error:
        return _adyen_error_response(error)

    response_body = response.message
    # Store session data in Flask session so the redirect handler can re-create
    # the AdyenCheckout instance after a 3DS redirect
    session["adyen_session_id"] = response_body.get("id")
    session["adyen_session_data"] = response_body.get("sessionData")

    return jsonify({"requestBody": request_body, "response": response_body})


@bp.route("/sessions/handleShopperRedirect", methods=["GET"])
def sessions_handle_shopper_redirect() -> Response:
    """Handle the redirect back from the issuer for sessions-based flows.

    After a 3DS redirect the shopper returns here with `redirectResult` and
    `sessionId` query params.  We render a lightweight page that re-creates
    the AdyenCheckout instance with the stored session, letting the SDK
    finalise the payment on the client side.
    """
    from checkout.config import CLIENT_KEY, ADYEN_ENVIRONMENT

    redirect_result = request.args.get("redirectResult", "")
    session_id = request.args.get("sessionId", "") or session.get("adyen_session_id", "")
    session_data = session.get("adyen_session_data", "")

    return render_template(
        "pages/sessions_redirect.html",
        client_key=CLIENT_KEY,
        environment=ADYEN_ENVIRONMENT,
        session_id=session_id,
        session_data=session_data,
        redirect_result=redirect_result,
    )
