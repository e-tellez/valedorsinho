from typing import Any

from app.ports.checkout_port import CheckoutGateway
from app.use_cases.checkout_service import CheckoutService


class FakeCheckoutGateway(CheckoutGateway):
    def __init__(self) -> None:
        self.payment_request: dict[str, Any] | None = None

    def get_payment_methods(self, request_body: dict[str, Any]) -> dict[str, Any]:
        return {}

    def make_payment(self, request_body: dict[str, Any]) -> dict[str, Any]:
        self.payment_request = request_body
        return {"resultCode": "Authorised"}

    def payment_details(self, request_body: dict[str, Any]) -> dict[str, Any]:
        return {}

    def create_session(self, request_body: dict[str, Any]) -> dict[str, Any]:
        return {}

    def disable_stored_method(self, request_body: dict[str, Any]) -> dict[str, Any]:
        return {}

    def create_apple_pay_session(self, request_body: dict[str, Any]) -> dict[str, Any]:
        return {"epochTimestamp": 1}


def test_create_payment_omits_unsupplied_billing_and_legacy_3ds_fields() -> None:
    gateway = FakeCheckoutGateway()
    service = CheckoutService(gateway, "MerchantECOM")

    service.create_payment(
        payment_method={"type": "scheme"},
        amount_value=1000,
        currency="MXN",
        country_code="MX",
        return_url="https://example.com/checkout/result",
        origin="https://example.com",
        shopper_ip="192.0.2.1",
        is_guest=True,
    )

    assert gateway.payment_request is not None
    assert "billingAddress" not in gateway.payment_request
    assert "authenticationData" not in gateway.payment_request
    assert "storePaymentMethod" not in gateway.payment_request


def test_apple_pay_payment_redacts_token_from_preview() -> None:
    gateway = FakeCheckoutGateway()
    service = CheckoutService(gateway, "MerchantECOM", app_url="https://example.com")

    result = service.create_apple_pay_payment(
        apple_pay_token="sensitive-token",
        amount_value=100000,
        installment_count=3,
    )

    assert gateway.payment_request is not None
    assert gateway.payment_request["paymentMethod"]["applePayToken"] == "sensitive-token"
    assert result["requestBody"]["paymentMethod"]["applePayToken"] == "[redacted]"
