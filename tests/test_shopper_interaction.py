from typing import Any

from app.domain.models.checkout import Amount, PaymentRequest


def _payment_body(
    payment_method: dict[str, Any], shopper_reference: str | None = None
) -> dict[str, Any]:
    request = PaymentRequest(
        merchant_account="MerchantECOM",
        reference="order-1",
        amount=Amount(value=1000, currency="MXN"),
        country_code="MX",
        payment_method=payment_method,
        return_url="https://example.com/checkout/result",
        origin="https://example.com",
        shopper_reference=shopper_reference,
        shopper_ip="192.0.2.1",
    )
    return request.model_dump(by_alias=True, exclude_none=True)


def test_new_cards_use_ecommerce_shopper_interaction() -> None:
    for shopper_reference in (None, "shopper-1"):
        body = _payment_body({"type": "scheme"}, shopper_reference)

        assert body["shopperInteraction"] == "Ecommerce"


def test_stored_cards_use_contauth_shopper_interaction() -> None:
    body = _payment_body(
        {"type": "scheme", "storedPaymentMethodId": "stored-1"}, "shopper-1"
    )

    assert body["shopperInteraction"] == "ContAuth"
