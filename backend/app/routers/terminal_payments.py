"""Terminal Payments API endpoints.

Proxies requests to the Adyen Management API for cascading terminal selection
(Company Account → Merchant Account → Store → Terminal) and sends payment
requests to terminals via the Adyen Terminal API (Cloud).
"""

import json
import logging
import os
from typing import Any

import requests as http_requests
from fastapi import APIRouter, HTTPException, Query, Request
import Adyen

from app.core.config import adyen_client
from app.services.terminal_decoder import decode_additional_response, extract_payment_summary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/terminal", tags=["terminal-payments"])


def _adyen_error_response(error: Adyen.AdyenError) -> None:
    """Raise an HTTPException from an Adyen SDK exception."""
    logger.error("Adyen Management API error: %s – %s", type(error).__name__, error)
    status_code = getattr(error, "status_code", 500) or 500
    raise HTTPException(status_code=status_code, detail=str(error))


# ---------------------------------------------------------------------------
# GET /api/terminal/merchants
# ---------------------------------------------------------------------------

@router.get("/merchants")
async def list_merchants(
    page_number: int | None = Query(default=None, alias="pageNumber"),
    page_size: str = Query(default="100", alias="pageSize"),
) -> dict[str, Any]:
    """Return merchant accounts accessible by the API credential."""
    query_params: dict[str, str] = {"pageSize": page_size}
    if page_number is not None:
        query_params["pageNumber"] = str(page_number)

    try:
        response = adyen_client.management.account_merchant_level_api.list_merchant_accounts(
            query_parameters=query_params,
        )
    except Adyen.AdyenError as error:
        _adyen_error_response(error)

    return response.message


# ---------------------------------------------------------------------------
# GET /api/terminal/stores
# ---------------------------------------------------------------------------

@router.get("/stores")
async def list_stores(
    merchant_id: str = Query(alias="merchantId"),
    page_number: int | None = Query(default=None, alias="pageNumber"),
    page_size: str = Query(default="100", alias="pageSize"),
) -> dict[str, Any]:
    """Return stores for a given merchant account."""
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
# GET /api/terminal/terminals
# ---------------------------------------------------------------------------

@router.get("/terminals")
async def list_terminals(
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
        response = adyen_client.management.terminals_terminal_level_api.list_terminals(
            query_parameters=query_params,
        )
    except Adyen.AdyenError as error:
        _adyen_error_response(error)

    return response.message


# ---------------------------------------------------------------------------
# POST /api/terminal/make-payment
# ---------------------------------------------------------------------------

TERMINAL_API_URLS = {
    "test": "https://terminal-api-test.adyen.com/sync",
    "live": "https://terminal-api-live.adyen.com/sync",
}


@router.post("/make-payment")
async def make_payment(request: Request) -> dict[str, Any]:
    """Send a payment request to a terminal via the Adyen Terminal API (Cloud).

    Expects the full SaleToPOIRequest JSON in the request body.
    """
    payment_request = await request.json()
    if not payment_request:
        raise HTTPException(status_code=400, detail="Request body is required")

    api_key = os.getenv("ADYEN_API_KEY", "")
    environment = os.getenv("ADYEN_ENVIRONMENT", "test")
    terminal_api_url = TERMINAL_API_URLS.get(environment, TERMINAL_API_URLS["test"])

    try:
        terminal_response = http_requests.post(
            terminal_api_url,
            json=payment_request,
            headers={
                "x-API-key": api_key,
                "Content-Type": "application/json",
            },
            timeout=300,
        )
    except http_requests.RequestException as error:
        logger.error("Terminal API request failed: %s", error)
        raise HTTPException(status_code=502, detail=str(error))

    try:
        response_body = terminal_response.json()
    except ValueError:
        logger.error(
            "Invalid JSON in terminal response (HTTP %s): %s",
            terminal_response.status_code, terminal_response.text[:500],
        )
        raise HTTPException(
            status_code=502,
            detail=f"Invalid JSON in terminal response: {terminal_response.text[:500]}",
        )

    # Log the response structure for debugging
    sal_resp = response_body.get("SaleToPOIResponse", {}) if isinstance(response_body, dict) else {}
    logger.info(
        "Terminal API response – HTTP %s, SaleToPOIResponse keys: %s, Result: %s",
        terminal_response.status_code,
        list(sal_resp.keys()) if sal_resp else "N/A",
        sal_resp.get("PaymentResponse", {}).get("Response", {}).get("Result", "N/A"),
    )

    if terminal_response.status_code >= 400:
        raise HTTPException(status_code=terminal_response.status_code, detail=response_body)

    return response_body


# ---------------------------------------------------------------------------
# POST /api/terminal/decode-response
# ---------------------------------------------------------------------------

@router.post("/decode-response")
async def decode_response(request: Request) -> dict[str, Any]:
    """Decode a terminal payment response and extract the payment summary.

    Expects the full SaleToPOIResponse JSON in the request body.
    This replaces the server-side decoding that was done in the Flask
    payment-result page route.
    """
    response_data = await request.json()

    success = False
    result_title = "Payment Failed"
    result_message = ""
    decoded_additional_response = None
    payment_summary: list[tuple[str, str]] = []

    logger.info(
        "Decode-response request keys: %s",
        list(response_data.keys()) if isinstance(response_data, dict) else type(response_data).__name__,
    )

    sal_response = response_data.get("SaleToPOIResponse", {}) if isinstance(response_data, dict) else {}
    poi_response = sal_response.get("PaymentResponse", {})

    if poi_response:
        response_block = poi_response.get("Response", {})
        result_text = response_block.get("Result", "")
        error_condition = response_block.get("ErrorCondition", "")
        success = result_text == "Success"
        result_title = "Payment Approved" if success else "Payment Declined"

        if not success and error_condition:
            result_message = f"ErrorCondition: {error_condition}"

        logger.info(
            "Payment Result=%s, ErrorCondition=%s, Success=%s",
            result_text, error_condition, success,
        )

        additional = response_block.get("AdditionalResponse", "")

        decoded_additional_response = decode_additional_response(additional)
        payment_summary = extract_payment_summary(decoded_additional_response, poi_response)
    elif "error" in response_data:
        result_title = "Error"
        result_message = response_data.get("error", "")
        logger.warning("Payment error response: %s", result_message)

    return {
        "success": success,
        "resultTitle": result_title,
        "resultMessage": result_message,
        "decodedAdditionalResponse": decoded_additional_response,
        "paymentSummary": [{"label": label, "value": value} for label, value in payment_summary],
    }
