"""Terminal fleet management use cases."""

from __future__ import annotations

import logging
from typing import Any

from app.ports.management_port import ManagementGateway

logger = logging.getLogger(__name__)


class TerminalFleetService:
    """Application service for terminal fleet operations."""

    def __init__(self, management_gateway: ManagementGateway) -> None:
        self._management_gateway = management_gateway

    def list_terminals(self, query_params: dict[str, str]) -> dict[str, Any]:
        return self._management_gateway.list_terminals(query_params)

    def list_stores(self, merchant_id: str, query_params: dict[str, str]) -> dict[str, Any]:
        return self._management_gateway.list_stores(merchant_id, query_params)

    def reassign_terminals(
        self,
        terminal_ids: list[str],
        store_id: str,
    ) -> dict[str, Any]:
        results: list[dict] = []
        for terminal_id in terminal_ids:
            try:
                self._management_gateway.reassign_terminal(terminal_id, store_id)
                results.append({"terminalId": terminal_id, "success": True})
            except Exception as error:
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
