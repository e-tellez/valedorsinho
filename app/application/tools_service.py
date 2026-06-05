"""Tools use cases — payload validation and vertical suggestions."""

from __future__ import annotations

from typing import Any

from app.domain.ports.validator_port import PayloadValidator


class ToolsService:
    """Application service for developer tools."""

    def __init__(
        self,
        validator: PayloadValidator,
        verticals: list[dict[str, Any]],
    ) -> None:
        self._validator = validator
        self._verticals = verticals

    def validate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        errors = self._validator.validate(payload)
        return {"valid": len(errors) == 0, "errors": errors}

    def get_verticals(self) -> list[dict[str, Any]]:
        return self._verticals
