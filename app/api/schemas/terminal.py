"""Request/Response DTOs for terminal endpoints (driving adapter layer)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class ReassignTerminalsBody(BaseModel):
    """Body sent by the frontend to POST /api/fleet/reassign."""

    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    terminal_ids: list[str]
    store_id: str
    merchant_id: str


class MakePaymentBody(BaseModel):
    """SaleToPOI request forwarded verbatim to the Adyen Terminal Cloud API.

    The top-level key is expected to be ``SaleToPOIRequest``.  Extra fields
    are allowed so that the full Adyen nexo EPAS structure passes through
    without being stripped by Pydantic.
    """

    model_config = {"extra": "allow"}

    SaleToPOIRequest: dict[str, Any]


class DecodeResponseBody(BaseModel):
    """A raw terminal response to decode.

    May contain a ``SaleToPOIResponse`` (successful/declined payment) or an
    ``error`` string (network / protocol error returned by the Terminal API).
    Extra fields are allowed to accommodate future Adyen response shapes.
    """

    model_config = {"extra": "allow"}

    SaleToPOIResponse: dict[str, Any] | None = None
    error: str | None = None
