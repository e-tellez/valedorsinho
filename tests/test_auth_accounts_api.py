from fastapi.testclient import TestClient

from app.api.dependencies import get_auth_service, get_current_user
from app.domain.models.auth import AdyenAccount, UserProfile, UserRole
from app.main import create_app


def _account(config_id: str, label: str, is_active: bool) -> AdyenAccount:
    return AdyenAccount(
        id=config_id,
        label=label,
        client_key="test_client",
        merchant_account="MerchantECOM",
        is_active=is_active,
        locked=False,
        api_key_configured=True,
    )


class FakeAuthService:
    def list_accounts(self, user: UserProfile) -> list[AdyenAccount]:
        return [_account("cfg-1", "Primary", True), _account("cfg-2", "Secondary", False)]

    def create_account(self, user, label, api_key, client_key, merchant_account) -> AdyenAccount:
        return _account("cfg-new", label, True)

    def update_account(self, user, config_id, label, api_key, client_key, merchant_account) -> AdyenAccount:
        return _account(config_id, label, False)

    def delete_account(self, user, config_id) -> None:
        return None

    def activate_account(self, user, config_id) -> AdyenAccount:
        return _account(config_id, "Primary", True)


class ForbiddenAuthService(FakeAuthService):
    def list_accounts(self, user):
        raise PermissionError("Only admin and im users can manage company accounts")

    def create_account(self, *args, **kwargs):
        raise PermissionError("Only admin and im users can manage company accounts")


class MissingAccountService(FakeAuthService):
    def update_account(self, *args, **kwargs):
        raise KeyError("Account not found")

    def activate_account(self, *args, **kwargs):
        raise KeyError("Account not found")


def _client(service_cls=FakeAuthService, role: UserRole = UserRole.ADMIN) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: UserProfile("me", "me@adyen.com", role)
    app.dependency_overrides[get_auth_service] = service_cls
    return TestClient(app)


def test_list_accounts_ok_and_hides_api_key() -> None:
    response = _client().get("/api/auth/accounts")
    assert response.status_code == 200
    body = response.json()
    assert body["accounts"][0] == {
        "id": "cfg-1",
        "label": "Primary",
        "clientKey": "test_client",
        "merchantAccount": "MerchantECOM",
        "isActive": True,
        "locked": False,
        "apiKeyConfigured": True,
    }
    assert "apiKey" not in body["accounts"][0]
    assert "api_key" not in response.text


def test_list_accounts_forbidden_for_user_role() -> None:
    response = _client(ForbiddenAuthService).get("/api/auth/accounts")
    assert response.status_code == 403


def test_create_account_ok() -> None:
    response = _client().post(
        "/api/auth/accounts",
        json={"label": "New", "apiKey": "AQE-secret", "clientKey": "test_client", "merchantAccount": "MerchantECOM"},
    )
    assert response.status_code == 200
    assert response.json()["isActive"] is True
    assert "AQE-secret" not in response.text


def test_create_account_forbidden_for_user_role() -> None:
    response = _client(ForbiddenAuthService).post(
        "/api/auth/accounts",
        json={"label": "New", "apiKey": "AQE", "clientKey": "ck", "merchantAccount": "MA"},
    )
    assert response.status_code == 403


def test_update_account_not_found_is_404() -> None:
    response = _client(MissingAccountService).put(
        "/api/auth/accounts/missing",
        json={"label": "X", "clientKey": "ck", "merchantAccount": "MA"},
    )
    assert response.status_code == 404


def test_activate_account_ok() -> None:
    response = _client().put("/api/auth/accounts/cfg-2/activate")
    assert response.status_code == 200
    assert response.json()["isActive"] is True


def test_activate_account_not_found_is_404() -> None:
    response = _client(MissingAccountService).put("/api/auth/accounts/missing/activate")
    assert response.status_code == 404


def test_delete_account_ok() -> None:
    response = _client().delete("/api/auth/accounts/cfg-2")
    assert response.status_code == 204
