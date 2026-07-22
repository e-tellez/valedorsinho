"""Pydantic schemas for webhook endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class WebhookSummary(BaseModel):
    id: str
    user_id: str | None = None
    merchant_account: str
    event_code: str
    psp_reference: str | None = None
    merchant_reference: str | None = None
    amount_value: int | None = None
    amount_currency: str | None = None
    success: bool | None = None
    live: bool
    received_at: datetime
    expires_at: datetime


class WebhookDetail(WebhookSummary):
    payload: dict[str, Any]


class WebhookListResponse(BaseModel):
    items: list[WebhookSummary]
