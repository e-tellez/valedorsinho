"""Tools API endpoints.

Payload validation against the Adyen OpenAPI spec and vertical
payload suggestions.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.data.verticals import VERTICALS
from app.services.validator import validate_payments_payload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tools", tags=["tools"])


# ---------------------------------------------------------------------------
# POST /api/tools/validate-payload
# ---------------------------------------------------------------------------

@router.post("/validate-payload")
async def validate_payload(request: Request) -> dict[str, Any]:
    """Validate a /payments JSON payload against the OpenAPI spec.

    Expects a JSON body with a ``payload`` key containing the raw
    /payments request object.  Returns validation errors (if any).
    """
    body = await request.json()
    if not body or "payload" not in body:
        raise HTTPException(status_code=400, detail="Request must include a 'payload' key.")

    payload = body["payload"]
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="'payload' must be a JSON object.")

    try:
        errors = validate_payments_payload(payload)
    except Exception as exception:
        logger.exception("Validation failed")
        raise HTTPException(status_code=500, detail=f"Validation error: {exception}")

    return {"valid": len(errors) == 0, "errors": errors}


# ---------------------------------------------------------------------------
# GET /api/tools/verticals
# ---------------------------------------------------------------------------

@router.get("/verticals")
async def get_verticals() -> list[dict[str, Any]]:
    """Return the list of merchant verticals with suggested payloads."""
    return VERTICALS
