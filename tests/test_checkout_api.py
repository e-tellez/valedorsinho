from typing import Any

from fastapi.testclient import TestClient

from app.api.dependencies import get_checkout_service, get_current_user
from app.domain.models.auth import UserProfile, UserRole
from app.main import create_app


class FakeCheckoutService:
    """Records the arguments passed to get_apple_pay_payment_methods."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def get_apple_pay_payment_methods(
        self, country_code: str = "MX", currency: str = "MXN"
    ) -> dict[str, Any]:
        self.calls.append((country_code, currency))
        return {"requestBody": {}, "response": {"paymentMethods": []}}


def _client(service: FakeCheckoutService) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: UserProfile(
        user_id="user-1",
        email="admin@adyen.com",
        role=UserRole.ADMIN,
    )
    app.dependency_overrides[get_checkout_service] = lambda: service
    return TestClient(app)


def test_apple_pay_payment_methods_without_body_defaults_to_mx_mxn() -> None:
    service = FakeCheckoutService()
    response = _client(service).post("/api/checkout/apple-pay/payment-methods")

    assert response.status_code == 200
    assert service.calls == [("MX", "MXN")]


def test_apple_pay_payment_methods_with_empty_object_defaults_to_mx_mxn() -> None:
    service = FakeCheckoutService()
    response = _client(service).post("/api/checkout/apple-pay/payment-methods", json={})

    assert response.status_code == 200
    assert service.calls == [("MX", "MXN")]


def test_apple_pay_payment_methods_forwards_explicit_values() -> None:
    service = FakeCheckoutService()
    response = _client(service).post(
        "/api/checkout/apple-pay/payment-methods",
        json={"countryCode": "US", "currency": "USD"},
    )

    assert response.status_code == 200
    assert service.calls == [("US", "USD")]


def test_apple_pay_payment_methods_body_is_optional_in_openapi() -> None:
    app = create_app()
    schema = app.openapi()
    operation = schema["paths"]["/api/checkout/apple-pay/payment-methods"]["post"]
    request_body = operation.get("requestBody", {})
    assert request_body.get("required", False) is False
