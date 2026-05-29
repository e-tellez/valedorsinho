"""Terminal Payments API endpoints.

Proxies requests to the Adyen Management API for cascading terminal selection:
Company Account → Merchant Account → Store → Terminal.
"""

import logging
import os

import requests as http_requests
from flask import Blueprint, Response, jsonify, request
import Adyen

from checkout.config import adyen_client

logger = logging.getLogger(__name__)

bp = Blueprint("terminal_payments_api", __name__, url_prefix="/terminal-payments")


def _adyen_error_response(error: Adyen.AdyenError) -> tuple[Response, int]:
    """Build a JSON error response from an Adyen SDK exception."""
    logger.error("Adyen Management API error: %s – %s", type(error).__name__, error)
    status_code = getattr(error, "status_code", 500) or 500
    return jsonify({"error": str(error), "type": type(error).__name__}), status_code


@bp.route("/api/merchants", methods=["GET"])
def list_merchants() -> tuple[Response, int] | Response:
    """Return merchant accounts accessible by the API credential.

    Query params forwarded to Adyen:
      - pageNumber  – 1-based page number
      - pageSize    – items per page (default 100)
    """
    query_params = {"pageSize": request.args.get("pageSize", "100")}
    page_number = request.args.get("pageNumber")
    if page_number:
        query_params["pageNumber"] = page_number

    try:
        response = adyen_client.management.account_merchant_level_api.list_merchant_accounts(
            query_parameters=query_params,
        )
    except Adyen.AdyenError as error:
        return _adyen_error_response(error)

    return jsonify(response.message)


@bp.route("/api/stores", methods=["GET"])
def list_stores() -> tuple[Response, int] | Response:
    """Return stores for a given merchant account.

    Query params:
      - merchantId  – required, the merchant account whose stores to list
      - pageNumber  – 1-based page number
      - pageSize    – items per page (default 100)
    """
    merchant_id = request.args.get("merchantId", "")
    if not merchant_id:
        return jsonify({"error": "merchantId query parameter is required"}), 400

    query_params = {"pageSize": request.args.get("pageSize", "100")}
    page_number = request.args.get("pageNumber")
    if page_number:
        query_params["pageNumber"] = page_number

    try:
        response = adyen_client.management.account_store_level_api.list_stores_by_merchant_id(
            merchantId=merchant_id,
            query_parameters=query_params,
        )
    except Adyen.AdyenError as error:
        return _adyen_error_response(error)

    return jsonify(response.message)


@bp.route("/api/terminals", methods=["GET"])
def list_terminals() -> tuple[Response, int] | Response:
    """Return terminals filtered by merchant and/or store.

    Query params forwarded to Adyen:
      - merchantIds  – comma-separated merchant account IDs
      - storeIds     – comma-separated store IDs
      - searchQuery  – filter by serial number / terminal ID
      - pageNumber   – 1-based page number
      - pageSize     – items per page (default 100)
    """
    query_params = {}
    for param in ("searchQuery", "merchantIds", "storeIds", "pageNumber", "pageSize"):
        value = request.args.get(param)
        if value:
            query_params[param] = value

    if not query_params.get("pageSize"):
        query_params["pageSize"] = "100"

    try:
        response = adyen_client.management.terminals_terminal_level_api.list_terminals(
            query_parameters=query_params,
        )
    except Adyen.AdyenError as error:
        return _adyen_error_response(error)

    return jsonify(response.message)


TERMINAL_API_URLS = {
    "test": "https://terminal-api-test.adyen.com/sync",
    "live": "https://terminal-api-live.adyen.com/sync",
}


@bp.route("/api/make-payment", methods=["POST"])
def make_payment() -> tuple[Response, int] | Response:
    """Send a payment request to a terminal via the Adyen Terminal API (Cloud).

    Expects the full SaleToPOIRequest JSON in the request body.
    """
    payment_request = request.get_json(silent=True)
    if not payment_request:
        return jsonify({"error": "Request body is required"}), 400

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
        return jsonify({"error": str(error), "type": "RequestException"}), 502

    try:
        response_body = terminal_response.json()
    except ValueError:
        logger.error(
            "Invalid JSON in terminal response (HTTP %s): %s",
            terminal_response.status_code, terminal_response.text[:500],
        )
        return jsonify({
            "error": "Invalid JSON in terminal response",
            "raw": terminal_response.text[:500],
        }), 502

    # Log the response structure for debugging (keys only to avoid leaking data)
    sal_resp = response_body.get("SaleToPOIResponse", {}) if isinstance(response_body, dict) else {}
    logger.info(
        "Terminal API response – HTTP %s, SaleToPOIResponse keys: %s, Result: %s",
        terminal_response.status_code,
        list(sal_resp.keys()) if sal_resp else "N/A",
        sal_resp.get("PaymentResponse", {}).get("Response", {}).get("Result", "N/A"),
    )

    if terminal_response.status_code >= 400:
        return jsonify(response_body), terminal_response.status_code

    return jsonify(response_body)
