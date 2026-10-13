"""Port for authentication and per-user Adyen credential management (driven side)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.auth import (
    AdyenAccount,
    AdyenCredentials,
    ManagedUser,
    UserProfile,
    UserRole,
)


class AuthGateway(ABC):
    """Interface for verifying identity and managing per-user Adyen credentials."""

    @abstractmethod
    def verify_token(self, token: str) -> UserProfile:
        """Verify a Supabase JWT and return the authenticated user's profile."""
        ...

    # ------------------------------------------------------------------
    # Active Adyen credentials (used to actually talk to Adyen)
    # ------------------------------------------------------------------

    @abstractmethod
    def get_adyen_config(self, user_id: str) -> AdyenCredentials | None:
        """Return the user's *active* Adyen credentials, or None if none is set.

        Resolves the account pointed to by ``profiles.active_adyen_config_id``.
        """
        ...

    @abstractmethod
    def upsert_adyen_config(self, user_id: str, credentials: AdyenCredentials) -> AdyenCredentials:
        """Create or update the user's *active* Adyen credentials row.

        When the user has no account yet, create one and make it active.

        Raises:
            PermissionError: if the active row has ``locked = true``.
        """
        ...

    # ------------------------------------------------------------------
    # Multiple saved company accounts
    # ------------------------------------------------------------------

    @abstractmethod
    def list_adyen_configs(self, user_id: str) -> list[AdyenAccount]:
        """Return all saved Adyen accounts for *user_id* (never the API key)."""
        ...

    @abstractmethod
    def create_adyen_config(
        self, user_id: str, label: str, credentials: AdyenCredentials
    ) -> AdyenAccount:
        """Create a new saved account. The first account becomes active."""
        ...

    @abstractmethod
    def update_adyen_config(
        self,
        user_id: str,
        config_id: str,
        label: str,
        api_key: str | None,
        client_key: str,
        merchant_account: str,
    ) -> AdyenAccount:
        """Update a specific account owned by *user_id*.

        A blank *api_key* preserves the existing stored key.

        Raises:
            PermissionError: if the row is locked.
            KeyError: if the account does not exist for this user.
        """
        ...

    @abstractmethod
    def delete_adyen_config(self, user_id: str, config_id: str) -> None:
        """Delete a specific account owned by *user_id*.

        Raises:
            PermissionError: if the row is locked.
            KeyError: if the account does not exist for this user.
        """
        ...

    @abstractmethod
    def set_active_adyen_config(self, user_id: str, config_id: str) -> AdyenAccount:
        """Mark *config_id* as the active account for *user_id*.

        Raises:
            KeyError: if the account does not exist for this user.
        """
        ...

    # ------------------------------------------------------------------
    # User & role administration
    # ------------------------------------------------------------------

    @abstractmethod
    def list_users(self) -> list[ManagedUser]:
        """Return every known user with their role (admin panel)."""
        ...

    @abstractmethod
    def update_user_role(self, user_id: str, role: UserRole) -> ManagedUser:
        """Set *user_id*'s role and return the updated user."""
        ...
