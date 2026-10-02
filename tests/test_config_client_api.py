from fastapi.testclient import TestClient

from app.api.dependencies import get_auth_service, get_current_user
from app.domain.models.auth import AdyenCredentials, UserProfile, UserRole
from app.main import create_app


class _ConfigAuthService:
    """Auth service stub that resolves to a fixed set of credentials."""

    def __init__(self, credentials: AdyenCredentials) -> None:
        self._credentials = credentials

    def resolve_credentials(self, user: UserProfile) -> AdyenCredentials:
        return self._credentials


def _client_with_credentials(credentials: AdyenCredentials) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: UserProfile(
        user_id="user-1",
        email="admin@adyen.com",
        role=UserRole.ADMIN,
    )
    app.dependency_overrides[get_auth_service] = lambda: _ConfigAuthService(credentials)
    return TestClient(app)


def test_get_client_config_returns_camel_case_without_api_key() -> None:
    client = _client_with_credentials(
        AdyenCredentials(
            api_key="AQE-secret-value",
            client_key="test_client",
            merchant_account="MerchantECOM",
            environment="test",
        )
    )

    response = client.get("/api/config/client")

    assert response.status_code == 200
    assert response.json() == {
        "clientKey": "test_client",
        "environment": "test",
        "merchantAccount": "MerchantECOM",
    }
    assert "AQE-secret-value" not in response.text


def test_get_client_config_returns_404_for_blank_client_key() -> None:
    client = _client_with_credentials(
        AdyenCredentials(
            api_key="AQE-secret-value",
            client_key="   ",
            merchant_account="MerchantECOM",
            environment="test",
        )
    )

    response = client.get("/api/config/client")

    assert response.status_code == 404
    assert "AQE-secret-value" not in response.text


def test_get_client_config_returns_404_for_blank_merchant_account() -> None:
    client = _client_with_credentials(
        AdyenCredentials(
            api_key="AQE-secret-value",
            client_key="test_client",
            merchant_account="",
            environment="test",
        )
    )

    response = client.get("/api/config/client")

    assert response.status_code == 404
    assert "AQE-secret-value" not in response.text
