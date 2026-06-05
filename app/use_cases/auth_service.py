"""Auth use case — JWT verification and per-request credential resolution."""

from __future__ import annotations

from app.domain.models.auth import AdyenCredentials, UserProfile, UserRole
from app.ports.auth_port import AuthGateway


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

        - admin / im  →  personal credentials from Supabase; falls back to default.
        - user        →  shared default credentials from env vars.
        """
        if user.role in (UserRole.ADMIN, UserRole.IM):
            personal_credentials = self._gateway.get_adyen_config(user.user_id)
            if personal_credentials is not None:
                return personal_credentials
        return self._default_credentials

    def get_user_config(self, user: UserProfile) -> AdyenCredentials | None:
        """Return the stored config for admin/im users; None for user role."""
        if user.role not in (UserRole.ADMIN, UserRole.IM):
            return None
        return self._gateway.get_adyen_config(user.user_id)

    def save_user_config(
        self, user: UserProfile, credentials: AdyenCredentials
    ) -> AdyenCredentials:
        """Persist credentials for admin/im users.

        Raises:
            PermissionError: if the role is 'user' or the existing config is locked.
        """
        if user.role not in (UserRole.ADMIN, UserRole.IM):
            raise PermissionError("Only admin and im users can set custom credentials")
        return self._gateway.upsert_adyen_config(user.user_id, credentials)
