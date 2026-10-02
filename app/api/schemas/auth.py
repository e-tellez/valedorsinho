"""Pydantic schemas for auth credential endpoints."""

from __future__ import annotations

from pydantic import BaseModel
from pydantic.alias_generators import to_camel

from app.domain.models.auth import UserRole


class AdyenConfigResponse(BaseModel):
    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    role: UserRole
    client_key: str
    merchant_account: str
    environment: str
    is_custom: bool
    locked: bool
    api_key_configured: bool
    can_configure: bool


class UpsertAdyenConfigBody(BaseModel):
    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    api_key: str | None = None
    client_key: str
    merchant_account: str
