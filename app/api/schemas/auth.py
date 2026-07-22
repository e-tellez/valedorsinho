"""Pydantic schemas for auth credential endpoints."""

from __future__ import annotations

from pydantic import BaseModel

from app.domain.models.auth import UserRole


class AdyenConfigResponse(BaseModel):
    role: UserRole
    client_key: str
    merchant_account: str
    environment: str
    is_custom: bool
    locked: bool


class UpsertAdyenConfigBody(BaseModel):
    api_key: str
    client_key: str
    merchant_account: str
