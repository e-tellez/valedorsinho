"""Terminal Fleet Manager API endpoints.

Proxies requests to the Adyen Management API so the browser can list
terminals and inspect their store / merchant assignments.
"""

import logging

from flask import Blueprint, Response, jsonify, request
import Adyen

from checkout.config import adyen_client

logger = logging.getLogger(__name__)

bp = Blueprint("terminal_fleet_api", __name__, url_prefix="/terminal-fleet")


def _adyen_error_response(error: Adyen.AdyenError) -> tuple[Response, int]:
    """Build a JSON error response from an Adyen SDK exception."""
    logger.error("Adyen Management API error: %s – %s", type(error).__name__, error)
    status_code = getattr(error, "status_code", 500) or 500
    return jsonify({"error": str(error), "type": type(error).__name__}), status_code


@bp.route("/api/terminals", methods=["GET"])
def list_terminals() -> tuple[Response, int] | Response:
    """Return a paginated list of terminals from the Adyen Management API.

    Query params forwarded to Adyen:
      - searchQuery   – filter by serial number / terminal ID
      - merchantIds   – comma-separated merchant account IDs
      - storeIds      – comma-separated store IDs
      - countries      – comma-separated country codes
      - brandModels   – comma-separated brand/model strings
      - pageNumber    – 1-based page number (default 1)
      - pageSize      – items per page (default 20)
    """
    query_params = {}
    for param in ("searchQuery", "merchantIds", "storeIds", "countries",
                  "brandModels", "pageNumber", "pageSize"):
        value = request.args.get(param)
        if value:
            query_params[param] = value

    try:
        response = adyen_client.management.terminals_terminal_level_api.list_terminals(
            query_parameters=query_params,
        )
    except Adyen.AdyenError as error:
        return _adyen_error_response(error)

    return jsonify(response.message)


@bp.route("/api/stores", methods=["GET"])
def list_stores() -> tuple[Response, int] | Response:
    """Return all stores for a given merchant so we can resolve store names.

    Query params:
      - merchantId – the merchant account ID whose stores to list
      - pageNumber – 1-based page number (default 1)
      - pageSize   – items per page (default 100)
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


@bp.route("/api/reassign", methods=["POST"])
def reassign_terminals() -> tuple[Response, int] | Response:
    """Reassign one or more terminals to a different store.

    Expected JSON body:
      - terminalIds  – list of terminal ID strings to reassign
      - storeId      – the target store to move the terminals to
      - merchantId   – the merchant account that owns the terminals
    """
    payload = request.get_json(silent=True) or {}
    terminal_ids = payload.get("terminalIds", [])
    store_id = payload.get("storeId", "")
    merchant_id = payload.get("merchantId", "")

    if not terminal_ids:
        return jsonify({"error": "terminalIds is required and must not be empty"}), 400
    if not store_id:
        return jsonify({"error": "storeId is required"}), 400
    if not merchant_id:
        return jsonify({"error": "merchantId is required"}), 400

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
    return jsonify({
        "results": results,
        "summary": f"{successful}/{len(results)} terminals reassigned successfully",
    })
