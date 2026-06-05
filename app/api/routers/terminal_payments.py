"""Terminal Payments API router — driving adapter.

Thin HTTP layer for terminal selection cascades and Cloud Terminal API payments.
"""

import logging
from typing import Any

import Adyen
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.dependencies import get_terminal_payment_service
from app.use_cases.terminal_payment_service import TerminalPaymentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/terminal", tags=["terminal-payments"])


def _handle_adyen_error(error: Adyen.AdyenError) -> None:
    logger.error("Adyen Management API error: %s – %s", type(error).__name__, error)
    status_code = getattr(error, "status_code", 500) or 500
    raise HTTPException(status_code=status_code, detail=str(error))


# ---------------------------------------------------------------------------
# GET /api/terminal/merchants
# ---------------------------------------------------------------------------

@router.get("/merchants")
async def list_merchants(
    service: TerminalPaymentService = Depends(get_terminal_payment_service),
    page_number: int | None = Query(default=None, alias="pageNumber"),
    page_size: str = Query(default="100", alias="pageSize"),
) -> dict[str, Any]:
    """Return merchant accounts accessible by the API credential."""
    query_params: dict[str, str] = {"pageSize": page_size}
    if page_number is not None:
        query_params["pageNumber"] = str(page_number)
    try:
        return service.list_merchants(query_params)
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)


# ---------------------------------------------------------------------------
# GET /api/terminal/stores
# ---------------------------------------------------------------------------

@router.get("/stores")
async def list_stores(
    merchant_id: str = Query(alias="merchantId"),
    service: TerminalPaymentService = Depends(get_terminal_payment_service),
    page_number: int | None = Query(default=None, alias="pageNumber"),
    page_size: str = Query(default="100", alias="pageSize"),
) -> dict[str, Any]:
    """Return stores for a given merchant account."""
    query_params: dict[str, str] = {"pageSize": page_size}
    if page_number is not None:
        query_params["pageNumber"] = str(page_number)
    try:
        return service.list_stores(merchant_id, query_params)
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)


# ---------------------------------------------------------------------------
# GET /api/terminal/terminals
# ---------------------------------------------------------------------------

@router.get("/terminals")
async def list_terminals(
    service: TerminalPaymentService = Depends(get_terminal_payment_service),
    search_query: str | None = Query(default=None, alias="searchQuery"),
    merchant_ids: str | None = Query(default=None, alias="merchantIds"),
    store_ids: str | None = Query(default=None, alias="storeIds"),
    page_number: int | None = Query(default=None, alias="pageNumber"),
    page_size: str = Query(default="100", alias="pageSize"),
) -> dict[str, Any]:
    """Return terminals filtered by merchant and/or store."""
    query_params: dict[str, str] = {"pageSize": page_size}
    if search_query:
        query_params["searchQuery"] = search_query
    if merchant_ids:
        query_params["merchantIds"] = merchant_ids
    if store_ids:
        query_params["storeIds"] = store_ids
    if page_number is not None:
        query_params["pageNumber"] = str(page_number)
    try:
        return service.list_terminals(query_params)
    except Adyen.AdyenError as error:
        _handle_adyen_error(error)


# ---------------------------------------------------------------------------
# POST /api/terminal/make-payment
# ---------------------------------------------------------------------------

@router.post("/make-payment")
async def make_payment(
    request: Request,
    service: TerminalPaymentService = Depends(get_terminal_payment_service),
) -> dict[str, Any]:
    """Send a payment request to a terminal via the Adyen Terminal API (Cloud)."""
    payment_request = await request.json()
    if not payment_request:
        raise HTTPException(status_code=400, detail="Request body is required")
    return service.make_payment(payment_request)


# ---------------------------------------------------------------------------
# POST /api/terminal/decode-response
# ---------------------------------------------------------------------------

@router.post("/decode-response")
async def decode_response(
    request: Request,
    service: TerminalPaymentService = Depends(get_terminal_payment_service),
) -> dict[str, Any]:
    """Decode a terminal payment response and extract the payment summary."""
    response_data = await request.json()
    result = service.decode_response(response_data)
    return {
        "success": result.success,
        "resultTitle": result.result_title,
        "resultMessage": result.result_message,
        "decodedAdditionalResponse": result.decoded_additional_response,
        "paymentSummary": [
            {"label": field.label, "value": field.value}
            for field in result.payment_summary
        ],
    }
