"""Webhook domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class WebhookEvent:
    """A single Adyen notification item stored for a user."""

    merchant_account: str
    event_code: str
    payload: dict
    live: bool
    psp_reference: str | None = None
    merchant_reference: str | None = None
    amount_value: int | None = None
    amount_currency: str | None = None
    success: bool | None = None
    user_id: str | None = None
    id: str | None = None
    received_at: datetime | None = None
    expires_at: datetime | None = None
