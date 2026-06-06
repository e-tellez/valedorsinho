"""Port for webhook storage and retrieval (driven side)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.auth import UserRole
from app.domain.models.webhook import WebhookEvent


class WebhookGateway(ABC):
    """Interface for persisting and querying webhook events."""

    @abstractmethod
    def get_user_role(self, user_id: str) -> UserRole | None:
        """Return the role for *user_id*, or None if the user does not exist."""
        ...

    @abstractmethod
    def store_webhook(self, event: WebhookEvent) -> WebhookEvent:
        """Persist a webhook event and return it with server-assigned id and timestamps."""
        ...

    @abstractmethod
    def list_webhooks(self, user_id: str, limit: int, offset: int) -> list[WebhookEvent]:
        """Return non-expired webhooks for *user_id*, ordered by received_at descending."""
        ...

    @abstractmethod
    def get_webhook(self, webhook_id: str, user_id: str) -> WebhookEvent | None:
        """Return a single non-expired webhook owned by *user_id*, or None if not found."""
        ...

    @abstractmethod
    def delete_expired_webhooks(self) -> int:
        """Delete all rows where expires_at < now(). Returns the count of deleted rows."""
        ...
