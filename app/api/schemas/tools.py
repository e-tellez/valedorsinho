"""Request/Response DTOs for tools endpoints (driving adapter layer)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ValidatePayloadBody(BaseModel):
    """Body sent by the frontend to POST /api/tools/validate-payload."""

    payload: dict[str, Any]


class PayloadSuggestedBody(BaseModel):
    """Body sent by the frontend to POST /api/tools/payload-suggested."""

    verticals: list[str]
