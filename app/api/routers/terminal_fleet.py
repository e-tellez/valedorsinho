"""Terminal Fleet Manager API router — driving adapter."""

import logging
from typing import Any

import Adyen
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_terminal_fleet_service
from app.api.schemas.terminal import ReassignTerminalsBody
from app.application.terminal_fleet_service import TerminalFleetService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/fleet", tags=["terminal-fleet"])


def _handle_adyen_error(error: Adyen.AdyenError) -> None:
    logger.error("Adyen Management API error: %s – %s", type(error).__name__, error)
    status_code = getattr(error, "status_code", 500) or 500
    raise HTTPException(status_code=status_code, detail=str(error))


# ---------------------------------------------------------------------------
# GET /api/fleet/terminals
# ---------------------------------------------------------------------------

@router.get("/terminals")
async def list_terminals(
    service: TerminalFleetService = Depends(get_terminal_fleet_service),
    search_query: str | None = Query(default=None, alias="searchQuery"),
    merchant_ids: str | None = Query(default=None, alias="merchantIds"),
    store_ids: str | None = Query(default=None, alias="storeIds"),
    countries: str | None = Query(default=None),
    brand_models: str | None = Query(default=None, alias="brandModels"),
    page_number: int | None = Query(default=None, alias="pageNumber"),
    page_size: str | None = Query(default=None, alias="pageSize"),
) -> dict[str, Any]:
    """Return a paginated list of terminals from the Adyen Management API."""
    query_params: dict[str, str] = {}
    if search_query:
        query_params["searchQuery"] = search_query
    if merchant_ids:
        query_params["merchantIds"] = merchant_ids
    if store_ids:
        query_params["storeIds"] = store_ids
    if countries:
        query_params["countries"] = countries
    if brand_models:
        query_params["brandModels"] = brand_models
    if page_number is not None:
        query_params["pageNumber"] = str(page_number)
    if page_size:
        query_params["pageSize"] = page_size
    try:
        return service.list_terminals(query_params)
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)


# ---------------------------------------------------------------------------
# GET /api/fleet/stores
# ---------------------------------------------------------------------------

@router.get("/stores")
async def list_stores(
    merchant_id: str = Query(alias="merchantId"),
    service: TerminalFleetService = Depends(get_terminal_fleet_service),
    page_number: int | None = Query(default=None, alias="pageNumber"),
    page_size: str = Query(default="100", alias="pageSize"),
) -> dict[str, Any]:
    """Return all stores for a given merchant so we can resolve store names."""
    query_params: dict[str, str] = {"pageSize": page_size}
    if page_number is not None:
        query_params["pageNumber"] = str(page_number)
    try:
        return service.list_stores(merchant_id, query_params)
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)


# ---------------------------------------------------------------------------
# POST /api/fleet/reassign
# ---------------------------------------------------------------------------

@router.post("/reassign")
async def reassign_terminals(
    body: ReassignTerminalsBody,
    service: TerminalFleetService = Depends(get_terminal_fleet_service),
) -> dict[str, Any]:
    """Reassign one or more terminals to a different store."""
    if not body.terminal_ids:
        raise HTTPException(status_code=400, detail="terminalIds is required and must not be empty")
    return service.reassign_terminals(
        terminal_ids=body.terminal_ids,
        store_id=body.store_id,
    )
