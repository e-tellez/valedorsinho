import base64

from app.adapters.terminal_decoder import (
    decode_additional_response,
    extract_payment_summary,
)


def _b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def test_decodes_padded_base64_query_string() -> None:
    encoded = _b64("pspReference=123")
    assert encoded.endswith("==")  # guards against the parse_qs-first regression
    assert decode_additional_response(encoded) == {"pspReference": "123"}


def test_decodes_base64_json() -> None:
    encoded = _b64('{"pspReference": "abc", "authCode": "999"}')
    assert decode_additional_response(encoded) == {
        "pspReference": "abc",
        "authCode": "999",
    }


def test_decodes_base64_multi_field_query_string() -> None:
    encoded = _b64("pspReference=123&authCode=999&cardSummary=4764")
    assert decode_additional_response(encoded) == {
        "pspReference": "123",
        "authCode": "999",
        "cardSummary": "4764",
    }


def test_decodes_plain_query_string() -> None:
    assert decode_additional_response("pspReference=123&authCode=999") == {
        "pspReference": "123",
        "authCode": "999",
    }


def test_decodes_plain_json() -> None:
    assert decode_additional_response('{"pspReference": "abc"}') == {"pspReference": "abc"}


def test_bare_base64_token_decodes_as_base64_not_plain() -> None:
    # A bare alphanumeric token that is coincidentally valid Base64 must be
    # Base64-decoded (nexo EPAS), not returned as-is.
    encoded = _b64("pspReference=123")
    decoded = decode_additional_response(encoded)
    assert decoded == {"pspReference": "123"}


def test_empty_value_returns_none() -> None:
    assert decode_additional_response("") is None


def test_malformed_value_does_not_raise() -> None:
    # Not valid Base64, not JSON — must not raise. parse_qs is intentionally
    # lenient (keep_blank_values), so a bare token degrades to a dict rather
    # than exposing any known payment fields.
    decoded = decode_additional_response("!!!not-valid!!!")
    assert decoded is None or isinstance(decoded, (dict, str))
    assert extract_payment_summary(decoded) == []


def test_extract_payment_summary_from_decoded_psp_reference() -> None:
    decoded = decode_additional_response(_b64("pspReference=123"))
    summary = extract_payment_summary(decoded)
    assert ("PSP Reference", "123") in summary
