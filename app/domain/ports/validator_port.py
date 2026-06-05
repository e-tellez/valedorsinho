"""Port for payload validation (driven side)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PayloadValidator(ABC):
    """Abstract interface for validating Adyen payloads against a schema."""

    @abstractmethod
    def validate(self, payload: dict[str, Any]) -> list[dict[str, str]]:
        """Return a list of error dicts. Empty list means valid."""
        ...
