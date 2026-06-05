"""Port for authentication and per-user Adyen credential management (driven side)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.auth import AdyenCredentials, UserProfile


class AuthGateway(ABC):
    """Interface for verifying identity and managing per-user Adyen credentials."""

    @abstractmethod
    def verify_token(self, token: str) -> UserProfile:
        """Verify a Supabase JWT and return the authenticated user's profile."""
        ...

    @abstractmethod
    def get_adyen_config(self, user_id: str) -> AdyenCredentials | None:
        """Retrieve stored Adyen credentials for *user_id*, or None if unset."""
        ...

    @abstractmethod
    def upsert_adyen_config(self, user_id: str, credentials: AdyenCredentials) -> AdyenCredentials:
        """Create or update the Adyen credentials row for *user_id*.

        Raises:
            PermissionError: if the existing row has ``locked = true``.
        """
        ...
