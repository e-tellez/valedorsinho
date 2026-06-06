"""Webhook use case — ingest Adyen notifications and serve the webhook dashboard."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from app.domain.models.auth import UserProfile, UserRole
from app.domain.models.webhook import WebhookEvent
from app.ports.webhook_port import WebhookGateway

logger = logging.getLogger(__name__)

_RETENTION_DAYS: dict[UserRole, int] = {
    UserRole.ADMIN: 5,
    UserRole.IM: 3,
    UserRole.USER: 3,
}
_DEFAULT_RETENTION_DAYS = 3


class WebhookService:
    """Orchestrates webhook ingestion, retrieval, and cleanup."""

    def __init__(self, gateway: WebhookGateway) -> None:
        self._gateway = gateway

    def ingest_notification(self, payload: dict, user_id: str | None = None) -> list[WebhookEvent]:
        """Parse an Adyen notification payload and persist each notification item.

        *user_id* is taken from the webhook URL path so the owner is always known
        without querying adyen_configs. Adyen may batch multiple items in a single
        request — each is stored independently. Errors on individual items are logged
        and swallowed so the listener can always respond ``[accepted]``.
        """
        is_live = payload.get("live", "false") == "true"
        stored_events: list[WebhookEvent] = []

        role: UserRole | None = None
        if user_id is not None:
            role = self._gateway.get_user_role(user_id)

        retention_days = (
            _RETENTION_DAYS.get(role, _DEFAULT_RETENTION_DAYS)
            if role is not None
            else _DEFAULT_RETENTION_DAYS
        )
        expires_at = datetime.now(tz=timezone.utc) + timedelta(days=retention_days)

        for item in payload.get("notificationItems", []):
            notification = item.get("NotificationRequestItem", {})
            merchant_account = notification.get("merchantAccountCode", "")

            amount = notification.get("amount") or {}
            success_raw: str = notification.get("success", "false")

            event = WebhookEvent(
                user_id=user_id,
                merchant_account=merchant_account,
                event_code=notification.get("eventCode", ""),
                psp_reference=notification.get("pspReference") or None,
                merchant_reference=notification.get("merchantReference") or None,
                amount_value=amount.get("value"),
                amount_currency=amount.get("currency") or None,
                success=success_raw.lower() == "true",
                live=is_live,
                payload=notification,
                expires_at=expires_at,
            )

            try:
                stored_event = self._gateway.store_webhook(event)
                stored_events.append(stored_event)
                logger.info(
                    "Stored webhook event_code=%s merchant_account=%s psp_reference=%s",
                    event.event_code,
                    event.merchant_account,
                    event.psp_reference,
                )
            except Exception:
                logger.exception(
                    "Failed to store webhook for merchant account %s", merchant_account
                )

        return stored_events

    def list_user_webhooks(
        self, user: UserProfile, limit: int = 50, offset: int = 0
    ) -> list[WebhookEvent]:
        """Return non-expired webhooks for the authenticated user, newest first."""
        limit = min(limit, 100)
        return self._gateway.list_webhooks(
            user_id=user.user_id, limit=limit, offset=offset
        )

    def get_user_webhook(self, user: UserProfile, webhook_id: str) -> WebhookEvent:
        """Return a single webhook event.

        Raises:
            KeyError: if the webhook is not found or has expired.
        """
        event = self._gateway.get_webhook(
            webhook_id=webhook_id, user_id=user.user_id
        )
        if event is None:
            raise KeyError(f"Webhook {webhook_id} not found")
        return event

    def cleanup_expired(self) -> int:
        """Delete all expired webhook rows. Returns the count of deleted rows."""
        count = self._gateway.delete_expired_webhooks()
        logger.info("Deleted %d expired webhooks", count)
        return count
