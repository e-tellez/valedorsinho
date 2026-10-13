from fastapi.testclient import TestClient

from app.api.dependencies import get_auth_service, get_current_user
from app.domain.models.auth import ManagedUser, UserProfile, UserRole
from app.main import create_app


class FakeAuthService:
    def list_users(self, user: UserProfile) -> list[ManagedUser]:
        return [
            ManagedUser("u1", "admin@adyen.com", UserRole.ADMIN),
            ManagedUser("u2", "user@adyen.com", UserRole.USER),
        ]

    def set_user_role(self, user: UserProfile, target_user_id: str, role: UserRole) -> ManagedUser:
        return ManagedUser(target_user_id, "user@adyen.com", role)


class ForbiddenAuthService(FakeAuthService):
    def list_users(self, user: UserProfile) -> list[ManagedUser]:
        raise PermissionError("Only admin users can list users")

    def set_user_role(self, user: UserProfile, target_user_id: str, role: UserRole) -> ManagedUser:
        raise PermissionError("Only admin users can change roles")


class SelfDemotionAuthService(FakeAuthService):
    def set_user_role(self, user: UserProfile, target_user_id: str, role: UserRole) -> ManagedUser:
        raise ValueError("You cannot remove your own admin role")


def _client(service_cls=FakeAuthService, role: UserRole = UserRole.ADMIN) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: UserProfile("me", "me@adyen.com", role)
    app.dependency_overrides[get_auth_service] = service_cls
    return TestClient(app)


def test_list_users_ok() -> None:
    response = _client().get("/api/admin/users")
    assert response.status_code == 200
    body = response.json()
    assert body["users"][0] == {"userId": "u1", "email": "admin@adyen.com", "role": "admin"}
    assert body["users"][1]["role"] == "user"


def test_list_users_forbidden_for_non_admin() -> None:
    response = _client(ForbiddenAuthService).get("/api/admin/users")
    assert response.status_code == 403


def test_update_role_ok() -> None:
    response = _client().put("/api/admin/users/u2/role", json={"role": "im"})
    assert response.status_code == 200
    assert response.json() == {"userId": "u2", "email": "user@adyen.com", "role": "im"}


def test_update_role_invalid_value_is_422() -> None:
    response = _client().put("/api/admin/users/u2/role", json={"role": "superuser"})
    assert response.status_code == 422


def test_update_role_self_demotion_is_400() -> None:
    response = _client(SelfDemotionAuthService).put("/api/admin/users/me/role", json={"role": "user"})
    assert response.status_code == 400
