"""Port for Adyen Management API operations (driven side)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ManagementGateway(ABC):
    """Abstract interface for Adyen Management API operations."""

    @abstractmethod
    def list_merchant_accounts(self, query_params: dict[str, str]) -> dict[str, Any]:
        ...

    @abstractmethod
    def list_stores(self, merchant_id: str, query_params: dict[str, str]) -> dict[str, Any]:
        ...

    @abstractmethod
    def list_terminals(self, query_params: dict[str, str]) -> dict[str, Any]:
        ...

    @abstractmethod
    def reassign_terminal(self, terminal_id: str, store_id: str) -> dict[str, Any]:
        ...
