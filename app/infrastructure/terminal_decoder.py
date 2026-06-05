"""Terminal API AdditionalResponse decoder and payment summary extractor.

Pure infrastructure utility — no framework dependencies. Injected into
the TerminalPaymentService as function references.
"""

from __future__ import annotations

import base64
import json
from urllib.parse import parse_qs


def decode_additional_response(encoded_value: str) -> dict | str | None:
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


def extract_payment_summary(
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
