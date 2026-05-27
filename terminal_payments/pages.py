import base64
import json
from urllib.parse import parse_qs

from flask import Blueprint, render_template, request, session, url_for

bp = Blueprint("terminal_payments", __name__, url_prefix="/terminal-payments")


@bp.route("/")
def index() -> str:
    """Render the Terminal Payments page."""
    return render_template("pages/terminal_payments.html")


@bp.route("/make-payment")
def make_payment() -> str:
    """Render the Make a Payment placeholder."""
    return render_template("pages/terminal_make_payment.html")


@bp.route("/nfc")
def nfc_flow() -> str:
    """Render the NFC flow placeholder."""
    return render_template("pages/terminal_nfc.html")


@bp.route("/card-acquisition")
def card_acquisition() -> str:
    """Render the Card Acquisition flow placeholder."""
    return render_template("pages/terminal_card_acquisition.html")


@bp.route("/auth-capt")
def auth_capt() -> str:
    """Render the Auth-Capt flow placeholder."""
    return render_template("pages/terminal_auth_capt.html")


def _decode_additional_response(encoded_value: str) -> dict | str | None:
    """Decode a Base64-encoded AdditionalResponse (nexo EPAS / ISO 20022).

    The value is Base64-encoded per the nexo EPAS standard.
    Once decoded it may be a JSON object or a URL-encoded query string.
    Returns a dict, a plain string, or None if decoding fails.
    """
    if not encoded_value:
        return None
    try:
        decoded_bytes = base64.b64decode(encoded_value)
        decoded_string = decoded_bytes.decode("utf-8")
    except Exception:
        return None

    # Try JSON first
    try:
        return json.loads(decoded_string)
    except (json.JSONDecodeError, ValueError):
        pass

    # Fall back to URL-encoded query string
    try:
        parsed = parse_qs(decoded_string, keep_blank_values=True)
        if parsed:
            return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
    except Exception:
        pass

    # Return the raw decoded string if nothing else worked
    return decoded_string if decoded_string else None


@bp.route("/payment-result")
def payment_result() -> str:
    """Render the terminal payment result page."""
    terminal_id = request.args.get("terminalId", "")
    merchant_account = request.args.get("merchantAccount", "")

    response_data = session.pop("terminal_payment_response", None)
    if not response_data:
        response_data = {"error": "No payment response found in session."}

    # Determine success from the response
    success = False
    result_title = "Payment Failed"
    result_message = ""
    decoded_additional_response = None

    poi_response = (
        response_data
        .get("SaleToPOIResponse", {})
        .get("PaymentResponse", {})
    )
    if poi_response:
        result_text = poi_response.get("Response", {}).get("Result", "")
        success = result_text == "Success"
        result_title = "Payment Approved" if success else "Payment Declined"
        additional = poi_response.get("Response", {}).get("AdditionalResponse", "")

        # Decode the Base64-encoded AdditionalResponse (nexo EPAS standard)
        decoded_additional_response = _decode_additional_response(additional)
    elif "error" in response_data:
        result_title = "Error"
        result_message = response_data.get("error", "")

    back_url = url_for(
        "terminal_payments.make_payment",
        terminalId=terminal_id,
        merchantAccount=merchant_account,
    )

    return render_template(
        "pages/terminal_payment_result.html",
        success=success,
        result_title=result_title,
        result_message=result_message,
        response_json=json.dumps(response_data, indent=2),
        decoded_additional_response=decoded_additional_response,
        back_url=back_url,
    )
