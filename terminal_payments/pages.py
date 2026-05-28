import base64
import json
from urllib.parse import parse_qs

from flask import Blueprint, render_template, request, url_for

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
    """Decode an AdditionalResponse from the Terminal API.

    The value may be:
      - A plain URL-encoded query string (e.g. S1F2 terminals)
      - A Base64-encoded string (nexo EPAS standard) wrapping JSON
        or a URL-encoded query string (e.g. AMS1 terminals)
    Returns a dict, a plain string, or None if decoding fails.
    """
    if not encoded_value:
        return None

    def _try_parse(text: str) -> dict | None:
        """Try JSON then URL query-string parsing."""
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            pass
        try:
            parsed = parse_qs(text, keep_blank_values=True)
            if parsed:
                return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        except Exception:
            pass
        return None

    # 1) Try the raw value directly (plain query string or JSON)
    result = _try_parse(encoded_value)
    if result:
        return result

    # 2) Try Base64 decoding
    try:
        decoded_string = base64.b64decode(encoded_value).decode("utf-8")
    except Exception:
        return None

    result = _try_parse(decoded_string)
    if result:
        return result

    return decoded_string if decoded_string else None


_SUMMARY_FIELDS = [
    ("pspReference", "PSP Reference"),
    ("cardBin", "Card BIN"),
    ("cardSummary", "Card Summary"),
    ("cardType", "Card Type"),
    ("fundingSource", "Funding Source"),
    ("posEntryMode", "POS Entry Mode"),
]


def _extract_payment_summary(
    decoded: dict | str | None,
    poi_response: dict | None = None,
) -> list[tuple[str, str]]:
    """Extract key payment details from the decoded AdditionalResponse.

    Falls back to PaymentResult fields when AdditionalResponse is
    missing or incomplete (e.g. S1F2 terminals).
    Returns a list of (label, value) tuples for display.
    """
    flat: dict[str, str] = {}

    # 1) Pull from decoded AdditionalResponse (if available)
    if isinstance(decoded, dict):
        additional_data = decoded.get("additionalData", {})
        for key, _label in _SUMMARY_FIELDS:
            value = decoded.get(key) or additional_data.get(key) or ""
            if value:
                flat[key] = str(value)

    # 2) Fill gaps from PaymentResult in the POI response
    if poi_response:
        payment_result = poi_response.get("PaymentResult", {})

        # PSP Reference
        if "pspReference" not in flat:
            psp = (
                payment_result
                .get("PaymentAcquirerData", {})
                .get("AcquirerTransactionID", {})
                .get("TransactionID", "")
            )
            if psp:
                flat["pspReference"] = psp

        # Card data from MaskedPan  (e.g. "541333 **** 4764")
        card_data = (
            payment_result
            .get("PaymentInstrumentData", {})
            .get("CardData", {})
        )
        masked_pan_raw = card_data.get("MaskedPan", "")
        masked_pan = masked_pan_raw.get("PAN", "") if isinstance(masked_pan_raw, dict) else str(masked_pan_raw)
        if masked_pan:
            parts = masked_pan.replace("*", "").split()
            if "cardBin" not in flat and len(parts) >= 1:
                flat["cardBin"] = parts[0]
            if "cardSummary" not in flat and len(parts) >= 2:
                flat["cardSummary"] = parts[-1]

        # POS Entry Mode
        if "posEntryMode" not in flat:
            entry_mode = card_data.get("EntryMode", [])
            if entry_mode:
                flat["posEntryMode"] = ", ".join(entry_mode) if isinstance(entry_mode, list) else str(entry_mode)

        # Payment brand as cardType fallback
        if "cardType" not in flat:
            brand = card_data.get("PaymentBrand", "")
            if brand:
                flat["cardType"] = brand

    # Build ordered summary
    summary = []
    for key, label in _SUMMARY_FIELDS:
        value = flat.get(key, "")
        if value:
            summary.append((label, value))
    return summary


@bp.route("/payment-result", methods=["GET", "POST"])
def payment_result() -> str:
    """Render the terminal payment result page."""
    terminal_id = request.args.get("terminalId", "")
    merchant_account = request.args.get("merchantAccount", "")

    response_data = None
    if request.method == "POST":
        raw = request.form.get("response_data", "")
        if raw:
            try:
                response_data = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                response_data = None
    if not response_data:
        response_data = {"error": "No payment response found."}

    # Determine success from the response
    success = False
    result_title = "Payment Failed"
    result_message = ""
    decoded_additional_response = None
    payment_summary = []

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
        payment_summary = _extract_payment_summary(decoded_additional_response, poi_response)
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
        payment_summary=payment_summary,
        back_url=back_url,
    )
