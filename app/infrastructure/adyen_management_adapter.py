"""Adyen Management API adapter — implements ManagementGateway port."""

from __future__ import annotations

import logging
from typing import Any

import Adyen

from app.domain.ports.management_port import ManagementGateway

logger = logging.getLogger(__name__)


class AdyenManagementAdapter(ManagementGateway):
    """Concrete adapter that calls the Adyen Management API via the SDK."""

    def __init__(self, client: Adyen.Adyen) -> None:
        self._client = client

    def list_merchant_accounts(self, query_params: dict[str, str]) -> dict[str, Any]:
        response = self._client.management.account_merchant_level_api.list_merchant_accounts(
            query_parameters=query_params,
        )
        return response.message

    def list_stores(self, merchant_id: str, query_params: dict[str, str]) -> dict[str, Any]:
        response = self._client.management.account_store_level_api.list_stores_by_merchant_id(
            merchantId=merchant_id,
            query_parameters=query_params,
        )
        return response.message

    def list_terminals(self, query_params: dict[str, str]) -> dict[str, Any]:
        response = self._client.management.terminals_terminal_level_api.list_terminals(
            query_parameters=query_params,
        )
        return response.message

    def reassign_terminal(self, terminal_id: str, store_id: str) -> dict[str, Any]:
        reassignment_request = {"storeId": store_id}
        self._client.management.terminals_terminal_level_api.reassign_terminal(
            request=reassignment_request,
            terminalId=terminal_id,
        )
        return {"terminalId": terminal_id, "success": True}
