from flask import Blueprint, Response, request, jsonify, session, redirect, url_for

from checkout.config import adyen_client, MERCHANT_ACCOUNT
from checkout.helpers import generate_reference

bp = Blueprint("api", __name__)


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
    amount_minor_units = session.get("amount_minor_units", 1000)
    _cc = request.args.get("countryCode", "")
    _cur = request.args.get("currency", "")
    country_code = _cc if _cc and _cc != "undefined" else session.get("country_code", "MX")
    currency = _cur if _cur and _cur != "undefined" else session.get("currency", "MXN")
    shopper_locale = request.args.get("shopperLocale", "en-US")

    request_body = {
        "merchantAccount": MERCHANT_ACCOUNT,
        "amount": {
            "value": amount_minor_units,
            "currency": currency,
        },
        "countryCode": country_code,
        "shopperLocale": shopper_locale,
        "channel": "Web",
        # Include shopperReference so Adyen returns any stored (tokenised)
        # payment methods for this shopper.
        "shopperReference": session.get("shopper_reference", ""),
    }

    response = adyen_client.checkout.payments_api.payment_methods(request_body)
    return jsonify({"requestBody": request_body, "response": response.message})


@bp.route("/api/payments", methods=["POST"])
def payments() -> Response:
    """Initiate a payment.

    The browser sends the encrypted payment data (stateData.paymentMethod)
    collected by the Adyen Web Component.  We forward it to Adyen along with
    order details and 3DS2 / native 3DS parameters.
    """
    body = request.get_json()

    # Store the order reference in the server-side session so we can match
    # the /payments/details callback to the correct order later
    order_ref = generate_reference()
    session["order_ref"] = order_ref

    # Read the amount entered by the shopper (sent as minor units from the browser)
    # and fall back to $10.00 if not provided.
    amount_minor_units = session.get("amount_minor_units") or body.get("amountMinorUnits", 1000)
    currency = session.get("currency", "MXN")
    country_code = session.get("country_code", "MX")

    # Build the /payments request
    payment_request = {
        "merchantAccount": MERCHANT_ACCOUNT,
        "reference": order_ref,
        "amount": {
            "value": amount_minor_units,
            "currency": currency,
        },
        "countryCode": country_code,

        # ------------------------------------------------------------------
        # Payment method data – comes directly from the Drop-in / Component
        # ------------------------------------------------------------------
        "paymentMethod": body.get("paymentMethod"),

        # ------------------------------------------------------------------
        # 3DS2 / Native 3DS parameters
        # ------------------------------------------------------------------
        # "authenticationData" tells Adyen to attempt native 3DS2 (in-app /
        # in-browser authentication) before falling back to a redirect.
        "authenticationData": {
            "threeDSRequestData": {
                "nativeThreeDS": "preferred",
            },
        },

        "channel": "Web",
        "returnUrl": request.host_url + "dropin/handleShopperRedirect",
        "browserInfo": body.get("browserInfo"),
        "origin": request.host_url.rstrip("/"),

        # "additionalData": {
        #     "allow3DS2": "true",
        # },

        # ------------------------------------------------------------------
        # Tokenisation – CardOnFile with shopper consent
        # ------------------------------------------------------------------
        "shopperReference": session.get("shopper_reference", body.get("shopperReference", "shopper-001")),
        "recurringProcessingModel": "CardOnFile",
        # The Drop-in / Component shows a "Save for my next payment" checkbox
        # and sends storePaymentMethod: true/false in state.data.
        "storePaymentMethod": body.get("storePaymentMethod", False),
        # Ecommerce = shopper is present and using a new card
        # ContAuth   = shopper is using a previously stored (tokenised) card
        "shopperInteraction": "ContAuth" if body.get("paymentMethod", {}).get("storedPaymentMethodId") else "Ecommerce",

        # Shopper info – required by some issuers for 3DS2 risk scoring
        "shopperIP": request.remote_addr,
        "shopperEmail": body.get("shopperEmail", "shopper@example.com"),

        # Billing address – improves 3DS2 authorisation rates
        "billingAddress": body.get("billingAddress", {
            "street": "Teststreet 1",
            "houseNumberOrName": "1",
            "postalCode": "12345",
            "city": "Amsterdam",
            "stateOrProvince": "NH",
            "country": "NL",
        }),
    }

    # Send the payment request to Adyen
    response = adyen_client.checkout.payments_api.payments(payment_request)
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

    details_request = {
        # `details` contains the 3DS2 result data (e.g. threeDSResult,
        # fingerprint, or challengeResult) returned by the Web Component
        "details": body.get("details"),
    }

    # paymentData is the opaque string Adyen returned in the /payments
    # response; it must be sent back to tie the details to the payment
    payment_data = body.get("paymentData") or session.get("payment_data")
    if payment_data:
        details_request["paymentData"] = payment_data

    response = adyen_client.checkout.payments_api.payments_details(details_request)
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

    details_request = {
        "details": {
            # redirectResult is the encoded authentication outcome from the
            # issuer; passing it to /payments/details finalises the payment
            "redirectResult": redirect_result,
        },
        "paymentData": session.get("payment_data", ""),
    }

    response = adyen_client.checkout.payments_api.payments_details(details_request)
    result_code = response.message.get("resultCode", "")

    # Store the result in the session so /result can render a clean URL
    status = "success" if result_code in ("Authorised", "Pending", "Received") else "failure"
    session["payment_result"] = {
        "status": status,
        "result_code": result_code,
        "adyen_response": response.message if status == "success" else None,
        "integration_type": session.get("integration_type", "Unknown"),
    }
    return redirect(url_for("pages.result"))
