import pytest

from app.domain.models.auth import (
    AdyenAccount,
    AdyenCredentials,
    ManagedUser,
    UserProfile,
    UserRole,
)
from app.ports.auth_port import AuthGateway
from app.use_cases.auth_service import AuthService


class FakeAuthGateway(AuthGateway):
    """In-memory AuthGateway for exercising AuthService logic."""

    def __init__(self, credentials: AdyenCredentials | None = None) -> None:
        self.credentials = credentials
        self.accounts: dict[str, AdyenAccount] = {}
        self.active_id: str | None = None
        self.roles: dict[str, UserRole] = {}
        self._seq = 0

    def verify_token(self, token: str) -> UserProfile:  # pragma: no cover
        raise NotImplementedError

    def get_adyen_config(self, user_id: str) -> AdyenCredentials | None:
        return self.credentials

    def upsert_adyen_config(
        self, user_id: str, credentials: AdyenCredentials
    ) -> AdyenCredentials:
        self.credentials = credentials
        return credentials

    def list_adyen_configs(self, user_id: str) -> list[AdyenAccount]:
        return list(self.accounts.values())

    def create_adyen_config(
        self, user_id: str, label: str, credentials: AdyenCredentials
    ) -> AdyenAccount:
        self._seq += 1
        config_id = f"acct-{self._seq}"
        is_active = self.active_id is None
        account = AdyenAccount(
            id=config_id,
            label=label,
            client_key=credentials.client_key,
            merchant_account=credentials.merchant_account,
            is_active=is_active,
            locked=False,
            api_key_configured=bool(credentials.api_key),
        )
        self.accounts[config_id] = account
        if is_active:
            self.active_id = config_id
        return account

    def update_adyen_config(
        self,
        user_id: str,
        config_id: str,
        label: str,
        api_key: str | None,
        client_key: str,
        merchant_account: str,
    ) -> AdyenAccount:
        if config_id not in self.accounts:
            raise KeyError("Account not found")
        current = self.accounts[config_id]
        updated = AdyenAccount(
            id=config_id,
            label=label,
            client_key=client_key,
            merchant_account=merchant_account,
            is_active=current.is_active,
            locked=current.locked,
            api_key_configured=True,
        )
        self.accounts[config_id] = updated
        return updated

    def delete_adyen_config(self, user_id: str, config_id: str) -> None:
        if config_id not in self.accounts:
            raise KeyError("Account not found")
        del self.accounts[config_id]

    def set_active_adyen_config(self, user_id: str, config_id: str) -> AdyenAccount:
        if config_id not in self.accounts:
            raise KeyError("Account not found")
        self.active_id = config_id
        current = self.accounts[config_id]
        updated = AdyenAccount(
            id=current.id,
            label=current.label,
            client_key=current.client_key,
            merchant_account=current.merchant_account,
            is_active=True,
            locked=current.locked,
            api_key_configured=current.api_key_configured,
        )
        self.accounts[config_id] = updated
        return updated

    def list_users(self) -> list[ManagedUser]:
        return [
            ManagedUser(user_id=uid, email=f"{uid}@adyen.com", role=role)
            for uid, role in self.roles.items()
        ]

    def update_user_role(self, user_id: str, role: UserRole) -> ManagedUser:
        self.roles[user_id] = role
        return ManagedUser(user_id=user_id, email=f"{user_id}@adyen.com", role=role)


def _service(gateway: FakeAuthGateway) -> AuthService:
    return AuthService(
        auth_gateway=gateway,
        default_credentials=AdyenCredentials("default", "test_default", "Default", "test"),
    )


def _admin(user_id: str = "user-1") -> UserProfile:
    return UserProfile(user_id, "admin@adyen.com", UserRole.ADMIN)


# ---------------------------------------------------------------------------
# Active-account credential path
# ---------------------------------------------------------------------------

def test_update_user_config_preserves_write_only_api_key() -> None:
    gateway = FakeAuthGateway(
        AdyenCredentials(
            api_key="AQE-existing-secret",
            client_key="test_old",
            merchant_account="OldMerchant",
            environment="test",
        )
    )
    saved = _service(gateway).update_user_config(
        user=_admin(),
        api_key=None,
        client_key=" test_new ",
        merchant_account=" NewMerchant ",
    )

    assert saved.api_key == "AQE-existing-secret"
    assert saved.client_key == "test_new"
    assert saved.merchant_account == "NewMerchant"


# ---------------------------------------------------------------------------
# Multiple company accounts — role gating & validation
# ---------------------------------------------------------------------------

def test_list_accounts_requires_configuring_role() -> None:
    user = UserProfile("user-2", "user@adyen.com", UserRole.USER)
    with pytest.raises(PermissionError):
        _service(FakeAuthGateway()).list_accounts(user)


def test_create_account_validates_required_fields() -> None:
    with pytest.raises(ValueError):
        _service(FakeAuthGateway()).create_account(
            user=_admin(), label="A", api_key="", client_key="ck", merchant_account="MA"
        )


def test_create_account_first_one_is_active() -> None:
    gateway = FakeAuthGateway()
    account = _service(gateway).create_account(
        user=_admin(), label="Primary", api_key="AQE", client_key="ck", merchant_account="MA"
    )
    assert account.is_active is True
    assert account.api_key_configured is True


def test_activate_account_sets_active() -> None:
    gateway = FakeAuthGateway()
    service = _service(gateway)
    service.create_account(_admin(), "A", "AQE", "ck", "MA")
    second = service.create_account(_admin(), "B", "AQE2", "ck2", "MA2")
    assert second.is_active is False
    activated = service.activate_account(_admin(), second.id)
    assert activated.is_active is True


# ---------------------------------------------------------------------------
# User & role administration
# ---------------------------------------------------------------------------

def test_list_users_admin_only() -> None:
    im = UserProfile("user-3", "im@adyen.com", UserRole.IM)
    with pytest.raises(PermissionError):
        _service(FakeAuthGateway()).list_users(im)


def test_set_user_role_rejects_self_demotion() -> None:
    with pytest.raises(ValueError):
        _service(FakeAuthGateway()).set_user_role(_admin("me"), "me", UserRole.USER)


def test_set_user_role_non_admin_forbidden() -> None:
    im = UserProfile("user-3", "im@adyen.com", UserRole.IM)
    with pytest.raises(PermissionError):
        _service(FakeAuthGateway()).set_user_role(im, "someone", UserRole.ADMIN)


def test_set_user_role_updates_role() -> None:
    gateway = FakeAuthGateway()
    updated = _service(gateway).set_user_role(_admin(), "target", UserRole.IM)
    assert updated.role is UserRole.IM
    assert updated.user_id == "target"
