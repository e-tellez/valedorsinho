"""Tools API router — driving adapter."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_tools_service
from app.api.schemas.tools import PayloadSuggestedBody, ValidatePayloadBody
from app.use_cases.tools_service import ToolsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tools", tags=["tools"])


# ---------------------------------------------------------------------------
# POST /api/tools/validate-payload
# ---------------------------------------------------------------------------

@router.post("/validate-payload")
async def validate_payload(
    body: ValidatePayloadBody,
    service: ToolsService = Depends(get_tools_service),
) -> dict[str, Any]:
    """Validate a /payments JSON payload against the OpenAPI spec."""
    return service.validate_payload(body.payload)


# ---------------------------------------------------------------------------
# GET /api/tools/verticals
# ---------------------------------------------------------------------------

@router.get("/verticals")
async def get_verticals(
    service: ToolsService = Depends(get_tools_service),
) -> list[dict[str, Any]]:
    """Return the list of merchant verticals with suggested payloads."""
    return service.get_verticals()


# ---------------------------------------------------------------------------
# POST /api/tools/payload-suggested
# ---------------------------------------------------------------------------

@router.post("/payload-suggested")
async def get_payload_suggested(
    body: PayloadSuggestedBody,
    service: ToolsService = Depends(get_tools_service),
) -> dict[str, Any]:
    """Generate a suggested /payments payload for one or more merchant verticals."""
    try:
        return service.get_suggested_payload(body.verticals)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
