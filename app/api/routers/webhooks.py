"""Webhooks router — Adyen notification listener and webhook dashboard endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.api.dependencies import get_current_user, get_webhook_service
from app.api.schemas.webhook import WebhookDetail, WebhookListResponse, WebhookSummary
from app.domain.models.auth import UserProfile
from app.domain.models.webhook import WebhookEvent
from app.use_cases.webhook_service import WebhookService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


def _event_to_summary(event: WebhookEvent) -> WebhookSummary:
    return WebhookSummary(
        id=event.id,
        user_id=event.user_id,
        merchant_account=event.merchant_account,
        event_code=event.event_code,
        psp_reference=event.psp_reference,
        merchant_reference=event.merchant_reference,
        amount_value=event.amount_value,
        amount_currency=event.amount_currency,
        success=event.success,
        live=event.live,
        received_at=event.received_at,
        expires_at=event.expires_at,
    )


def _event_to_detail(event: WebhookEvent) -> WebhookDetail:
    return WebhookDetail(
        **_event_to_summary(event).model_dump(),
        payload=event.payload,
    )


@router.post("/adyen/{user_id}")
def receive_adyen_notification(
    user_id: str,
    payload: dict[str, Any],
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> JSONResponse:
    """Adyen notification listener. Always responds ``[accepted]`` per Adyen spec.

    *user_id* must match the Supabase profile id of the user who configured this
    webhook in Adyen. Using the user_id in the URL avoids a merchant account lookup
    and keeps routing stable even when credentials are rotated.
    """
    try:
        webhook_service.ingest_notification(payload, user_id=user_id)
    except Exception:
        logger.exception("Unexpected error while ingesting Adyen notification")
    return JSONResponse(content={"notificationResponse": "[accepted]"})


@router.get("", response_model=WebhookListResponse)
def list_webhooks(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: UserProfile = Depends(get_current_user),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> WebhookListResponse:
    """Return the authenticated user's non-expired webhooks, newest first."""
    events = webhook_service.list_user_webhooks(
        user=current_user, limit=limit, offset=offset
    )
    return WebhookListResponse(items=[_event_to_summary(e) for e in events])


@router.get("/{webhook_id}", response_model=WebhookDetail)
def get_webhook(
    webhook_id: str,
    current_user: UserProfile = Depends(get_current_user),
    webhook_service: WebhookService = Depends(get_webhook_service),
) -> WebhookDetail:
    """Return a single webhook event including the full raw payload."""
    try:
        event = webhook_service.get_user_webhook(
            user=current_user, webhook_id=webhook_id
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return _event_to_detail(event)
