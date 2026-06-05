"""Port for Terminal API Cloud operations (driven side)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TerminalGateway(ABC):
    """Abstract interface for Adyen Terminal API (Cloud) operations."""

    @abstractmethod
    def send_payment(self, sale_to_poi_request: dict[str, Any]) -> dict[str, Any]:
        ...
