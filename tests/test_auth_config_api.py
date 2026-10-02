from fastapi.testclient import TestClient

from app.api.dependencies import get_auth_service, get_current_user
from app.domain.models.auth import AdyenCredentials, UserProfile, UserRole
from app.main import create_app


class FakeAuthService:
    def get_user_config(self, user: UserProfile) -> AdyenCredentials | None:
        return AdyenCredentials(
            api_key="AQE-secret-value",
            client_key="test_client",
            merchant_account="MerchantECOM",
            environment="test",
            locked=False,
        )

    def resolve_credentials(self, user: UserProfile) -> AdyenCredentials:
        config = self.get_user_config(user)
        assert config is not None
        return config

    def update_user_config(
        self,
        user: UserProfile,
        api_key: str | None,
        client_key: str,
        merchant_account: str,
    ) -> AdyenCredentials:
        return AdyenCredentials(
            api_key=api_key or "AQE-existing-secret",
            client_key=client_key,
            merchant_account=merchant_account,
            environment="test",
        )


def test_get_config_returns_metadata_without_api_key() -> None:
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: UserProfile(
        user_id="user-1",
        email="admin@adyen.com",
        role=UserRole.ADMIN,
    )
    app.dependency_overrides[get_auth_service] = FakeAuthService

    response = TestClient(app).get("/api/auth/config")

    assert response.status_code == 200
    assert response.json() == {
        "role": "admin",
        "clientKey": "test_client",
        "merchantAccount": "MerchantECOM",
        "environment": "test",
        "isCustom": True,
        "locked": False,
        "apiKeyConfigured": True,
        "canConfigure": True,
    }
    assert "AQE-secret-value" not in response.text


def test_put_config_accepts_camel_case_and_does_not_echo_api_key() -> None:
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: UserProfile(
        user_id="user-1",
        email="admin@adyen.com",
        role=UserRole.ADMIN,
    )
    app.dependency_overrides[get_auth_service] = FakeAuthService

    response = TestClient(app).put(
        "/api/auth/config",
        json={
            "apiKey": "AQE-new-secret",
            "clientKey": "test_client",
            "merchantAccount": "MerchantECOM",
        },
    )

    assert response.status_code == 200
    assert response.json()["apiKeyConfigured"] is True
    assert "AQE-new-secret" not in response.text
