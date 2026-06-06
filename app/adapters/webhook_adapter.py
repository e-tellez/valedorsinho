"""Webhook adapter — implements WebhookGateway via Supabase REST API."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import requests as http_requests

from app.domain.models.auth import UserRole
from app.domain.models.webhook import WebhookEvent
from app.ports.webhook_port import WebhookGateway

logger = logging.getLogger(__name__)


class WebhookAdapter(WebhookGateway):
    """Concrete adapter that stores and retrieves webhook events via Supabase REST."""

    def __init__(self, supabase_url: str, service_role_key: str) -> None:
        self._base_url = supabase_url.rstrip("/")
        self._headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # WebhookGateway
    # ------------------------------------------------------------------

    def get_user_role(self, user_id: str) -> UserRole | None:
        response = http_requests.get(
            f"{self._base_url}/rest/v1/profiles",
            headers=self._headers,
            params={"id": f"eq.{user_id}", "select": "role", "limit": "1"},
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        if not rows:
            return None
        raw_role: str = rows[0].get("role", "user")
        try:
            return UserRole(raw_role)
        except ValueError:
            return UserRole.USER

    def store_webhook(self, event: WebhookEvent) -> WebhookEvent:
        body: dict[str, Any] = {
            "merchant_account": event.merchant_account,
            "event_code": event.event_code,
            "live": event.live,
            "payload": event.payload,
            "expires_at": event.expires_at.isoformat() if event.expires_at else None,
        }
        if event.user_id is not None:
            body["user_id"] = event.user_id
        if event.psp_reference is not None:
            body["psp_reference"] = event.psp_reference
        if event.merchant_reference is not None:
            body["merchant_reference"] = event.merchant_reference
        if event.amount_value is not None:
            body["amount_value"] = event.amount_value
        if event.amount_currency is not None:
            body["amount_currency"] = event.amount_currency
        if event.success is not None:
            body["success"] = event.success

        response = http_requests.post(
            f"{self._base_url}/rest/v1/webhooks",
            headers={**self._headers, "Prefer": "return=representation"},
            json=body,
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        return self._row_to_event(rows[0])

    def list_webhooks(self, user_id: str, limit: int, offset: int) -> list[WebhookEvent]:
        now = datetime.now(tz=timezone.utc).isoformat()
        response = http_requests.get(
            f"{self._base_url}/rest/v1/webhooks",
            headers=self._headers,
            params={
                "user_id": f"eq.{user_id}",
                "expires_at": f"gt.{now}",
                "order": "received_at.desc",
                "limit": str(limit),
                "offset": str(offset),
                "select": (
                    "id,user_id,merchant_account,event_code,psp_reference,"
                    "merchant_reference,amount_value,amount_currency,success,"
                    "live,received_at,expires_at"
                ),
            },
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        return [self._row_to_event(row) for row in rows]

    def get_webhook(self, webhook_id: str, user_id: str) -> WebhookEvent | None:
        now = datetime.now(tz=timezone.utc).isoformat()
        response = http_requests.get(
            f"{self._base_url}/rest/v1/webhooks",
            headers=self._headers,
            params={
                "id": f"eq.{webhook_id}",
                "user_id": f"eq.{user_id}",
                "expires_at": f"gt.{now}",
                "select": "*",
            },
            timeout=10,
        )
        response.raise_for_status()
        rows: list[dict[str, Any]] = response.json()
        if not rows:
            return None
        return self._row_to_event(rows[0])

    def delete_expired_webhooks(self) -> int:
        now = datetime.now(tz=timezone.utc).isoformat()
        response = http_requests.delete(
            f"{self._base_url}/rest/v1/webhooks",
            headers={
                **self._headers,
                "Prefer": "return=minimal,count=exact",
            },
            params={"expires_at": f"lt.{now}"},
            timeout=30,
        )
        response.raise_for_status()
        content_range = response.headers.get("Content-Range", "*/0")
        total_part = content_range.split("/")[-1]
        try:
            return int(total_part)
        except ValueError:
            return 0

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_event(row: dict[str, Any]) -> WebhookEvent:
        return WebhookEvent(
            id=row.get("id"),
            user_id=row.get("user_id"),
            merchant_account=row["merchant_account"],
            event_code=row["event_code"],
            psp_reference=row.get("psp_reference"),
            merchant_reference=row.get("merchant_reference"),
            amount_value=row.get("amount_value"),
            amount_currency=row.get("amount_currency"),
            success=row.get("success"),
            live=row.get("live", False),
            payload=row.get("payload", {}),
            received_at=(
                datetime.fromisoformat(row["received_at"])
                if row.get("received_at")
                else None
            ),
            expires_at=(
                datetime.fromisoformat(row["expires_at"])
                if row.get("expires_at")
                else None
            ),
        )
