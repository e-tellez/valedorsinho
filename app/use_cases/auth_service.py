"""Auth use case — JWT verification and per-request credential resolution."""

from __future__ import annotations

from app.domain.models.auth import (
    AdyenAccount,
    AdyenCredentials,
    ManagedUser,
    UserProfile,
    UserRole,
)
from app.ports.auth_port import AuthGateway

_CONFIGURING_ROLES = (UserRole.ADMIN, UserRole.IM)


class AuthService:
    """Orchestrates user authentication and Adyen credential resolution."""

    def __init__(
        self,
        auth_gateway: AuthGateway,
        default_credentials: AdyenCredentials,
    ) -> None:
        self._gateway = auth_gateway
        self._default_credentials = default_credentials

    def verify_token(self, token: str) -> UserProfile:
        return self._gateway.verify_token(token)

    def resolve_credentials(self, user: UserProfile) -> AdyenCredentials:
        """Return the Adyen credentials to use for this request.

        - admin / im  →  active personal account from Supabase; falls back to default.
        - user        →  shared default credentials from env vars.
        """
        if user.role in _CONFIGURING_ROLES:
            personal_credentials = self._gateway.get_adyen_config(user.user_id)
            if personal_credentials is not None:
                return personal_credentials
        return self._default_credentials

    def get_user_config(self, user: UserProfile) -> AdyenCredentials | None:
        """Return the active stored config for admin/im users; None for user role."""
        if user.role not in _CONFIGURING_ROLES:
            return None
        return self._gateway.get_adyen_config(user.user_id)

    def update_user_config(
        self,
        user: UserProfile,
        api_key: str | None,
        client_key: str,
        merchant_account: str,
    ) -> AdyenCredentials:
        if user.role not in _CONFIGURING_ROLES:
            raise PermissionError("Only admin and im users can set custom credentials")

        existing = self._gateway.get_adyen_config(user.user_id)
        resolved_api_key = api_key.strip() if api_key and api_key.strip() else ""
        if not resolved_api_key and existing is not None:
            resolved_api_key = existing.api_key

        resolved_client_key = client_key.strip()
        resolved_merchant_account = merchant_account.strip()
        if not resolved_api_key or not resolved_client_key or not resolved_merchant_account:
            raise ValueError("API key, client key, and merchant account are required")

        return self._gateway.upsert_adyen_config(
            user.user_id,
            AdyenCredentials(
                api_key=resolved_api_key,
                client_key=resolved_client_key,
                merchant_account=resolved_merchant_account,
                environment=self._default_credentials.environment,
            ),
        )

    # ------------------------------------------------------------------
    # Multiple saved company accounts (admin / im only)
    # ------------------------------------------------------------------

    def list_accounts(self, user: UserProfile) -> list[AdyenAccount]:
        self._require_configuring_role(user)
        return self._gateway.list_adyen_configs(user.user_id)

    def create_account(
        self,
        user: UserProfile,
        label: str,
        api_key: str | None,
        client_key: str,
        merchant_account: str,
    ) -> AdyenAccount:
        self._require_configuring_role(user)
        resolved_api_key = (api_key or "").strip()
        resolved_client_key = client_key.strip()
        resolved_merchant_account = merchant_account.strip()
        if not resolved_api_key or not resolved_client_key or not resolved_merchant_account:
            raise ValueError("API key, client key, and merchant account are required")
        return self._gateway.create_adyen_config(
            user.user_id,
            label.strip(),
            AdyenCredentials(
                api_key=resolved_api_key,
                client_key=resolved_client_key,
                merchant_account=resolved_merchant_account,
                environment=self._default_credentials.environment,
            ),
        )

    def update_account(
        self,
        user: UserProfile,
        config_id: str,
        label: str,
        api_key: str | None,
        client_key: str,
        merchant_account: str,
    ) -> AdyenAccount:
        self._require_configuring_role(user)
        resolved_client_key = client_key.strip()
        resolved_merchant_account = merchant_account.strip()
        if not resolved_client_key or not resolved_merchant_account:
            raise ValueError("Client key and merchant account are required")
        return self._gateway.update_adyen_config(
            user.user_id,
            config_id,
            label.strip(),
            api_key,
            resolved_client_key,
            resolved_merchant_account,
        )

    def delete_account(self, user: UserProfile, config_id: str) -> None:
        self._require_configuring_role(user)
        self._gateway.delete_adyen_config(user.user_id, config_id)

    def activate_account(self, user: UserProfile, config_id: str) -> AdyenAccount:
        self._require_configuring_role(user)
        return self._gateway.set_active_adyen_config(user.user_id, config_id)

    # ------------------------------------------------------------------
    # User & role administration (admin only)
    # ------------------------------------------------------------------

    def list_users(self, user: UserProfile) -> list[ManagedUser]:
        if user.role != UserRole.ADMIN:
            raise PermissionError("Only admin users can list users")
        return self._gateway.list_users()

    def set_user_role(
        self, user: UserProfile, target_user_id: str, role: UserRole
    ) -> ManagedUser:
        if user.role != UserRole.ADMIN:
            raise PermissionError("Only admin users can change roles")
        if target_user_id == user.user_id and role != UserRole.ADMIN:
            raise ValueError("You cannot remove your own admin role")
        return self._gateway.update_user_role(target_user_id, role)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _require_configuring_role(user: UserProfile) -> None:
        if user.role not in _CONFIGURING_ROLES:
            raise PermissionError("Only admin and im users can manage company accounts")
