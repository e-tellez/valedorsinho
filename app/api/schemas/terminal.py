"""Request/Response DTOs for terminal endpoints (driving adapter layer)."""

from __future__ import annotations

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class ReassignTerminalsBody(BaseModel):
    """Body sent by the frontend to POST /api/fleet/reassign."""

    model_config = {"alias_generator": to_camel, "populate_by_name": True}

    terminal_ids: list[str]
    store_id: str
    merchant_id: str
