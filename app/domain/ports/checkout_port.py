"""Port for checkout payment operations (driven side)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CheckoutGateway(ABC):
    """Abstract interface for Adyen Checkout API operations."""

    @abstractmethod
    def get_payment_methods(self, request_body: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def make_payment(self, request_body: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def payment_details(self, request_body: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def create_session(self, request_body: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def disable_stored_method(self, request_body: dict[str, Any]) -> dict[str, Any]:
        ...
