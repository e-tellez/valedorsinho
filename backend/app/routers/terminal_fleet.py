"""Terminal Fleet Manager API endpoints.

Proxies requests to the Adyen Management API so the frontend can list
terminals, inspect their store / merchant assignments, and reassign them.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
import Adyen

from app.core.config import adyen_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/fleet", tags=["terminal-fleet"])


def _adyen_error_response(error: Adyen.AdyenError) -> None:
    """Raise an HTTPException from an Adyen SDK exception."""
    logger.error("Adyen Management API error: %s – %s", type(error).__name__, error)
    status_code = getattr(error, "status_code", 500) or 500
    raise HTTPException(status_code=status_code, detail=str(error))


# ---------------------------------------------------------------------------
# GET /api/fleet/terminals
# ---------------------------------------------------------------------------

@router.get("/terminals")
async def list_terminals(
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
        response = adyen_client.management.terminals_terminal_level_api.list_terminals(
            query_parameters=query_params,
        )
    except Adyen.AdyenError as error:
        _adyen_error_response(error)

    return response.message


# ---------------------------------------------------------------------------
# GET /api/fleet/stores
# ---------------------------------------------------------------------------

@router.get("/stores")
async def list_stores(
    merchant_id: str = Query(alias="merchantId"),
    page_number: int | None = Query(default=None, alias="pageNumber"),
    page_size: str = Query(default="100", alias="pageSize"),
) -> dict[str, Any]:
    """Return all stores for a given merchant so we can resolve store names."""
    query_params: dict[str, str] = {"pageSize": page_size}
    if page_number is not None:
        query_params["pageNumber"] = str(page_number)

    try:
        response = adyen_client.management.account_store_level_api.list_stores_by_merchant_id(
            merchantId=merchant_id,
            query_parameters=query_params,
        )
    except Adyen.AdyenError as error:
        _adyen_error_response(error)

    return response.message


# ---------------------------------------------------------------------------
# POST /api/fleet/reassign
# ---------------------------------------------------------------------------

@router.post("/reassign")
async def reassign_terminals(request: Request) -> dict[str, Any]:
    """Reassign one or more terminals to a different store.

    Expected JSON body:
      - terminalIds  – list of terminal ID strings to reassign
      - storeId      – the target store to move the terminals to
      - merchantId   – the merchant account that owns the terminals
    """
    payload = await request.json()
    terminal_ids = payload.get("terminalIds", [])
    store_id = payload.get("storeId", "")
    merchant_id = payload.get("merchantId", "")

    if not terminal_ids:
        raise HTTPException(status_code=400, detail="terminalIds is required and must not be empty")
    if not store_id:
        raise HTTPException(status_code=400, detail="storeId is required")
    if not merchant_id:
        raise HTTPException(status_code=400, detail="merchantId is required")

    results: list[dict] = []
    for terminal_id in terminal_ids:
        reassignment_request = {
            "storeId": store_id,
        }
        try:
            adyen_client.management.terminals_terminal_level_api.reassign_terminal(
                request=reassignment_request,
                terminalId=terminal_id,
            )
            results.append({"terminalId": terminal_id, "success": True})
        except Adyen.AdyenError as error:
            logger.error("Failed to reassign terminal %s: %s", terminal_id, error)
            results.append({
                "terminalId": terminal_id,
                "success": False,
                "error": str(error),
            })

    successful = sum(1 for r in results if r["success"])
    return {
        "results": results,
        "summary": f"{successful}/{len(results)} terminals reassigned successfully",
    }
