"""Pydantic schemas for the multi-account management endpoints.

The secret API key is write-only: it is accepted on create/update but never
returned. Responses expose only ``apiKeyConfigured``.
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class AdyenAccountResponse(BaseModel):
    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    id: str
    label: str
    client_key: str
    merchant_account: str
    is_active: bool
    locked: bool
    api_key_configured: bool


class AccountListResponse(BaseModel):
    accounts: list[AdyenAccountResponse]


class CreateAccountBody(BaseModel):
    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    label: str = ""
    api_key: str
    client_key: str
    merchant_account: str


class UpdateAccountBody(BaseModel):
    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    label: str = ""
    api_key: str | None = None
    client_key: str
    merchant_account: str
