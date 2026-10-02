"""Tools use cases — payload validation and vertical suggestions."""

from __future__ import annotations

from typing import Any

from app.ports.validator_port import PayloadValidator


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge *overlay* into *base*, returning a new dict.

    - Nested dicts are merged recursively.
    - All other values (scalars, lists) use last-writer-wins (overlay wins).
    - Neither *base* nor *overlay* is mutated.
    """
    result = base.copy()
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ToolsService:
    """Application service for developer tools."""

    def __init__(
        self,
        validator: PayloadValidator,
        verticals: list[dict[str, Any]],
    ) -> None:
        self._validator = validator
        self._verticals = verticals
        self._vertical_index: dict[str, dict[str, Any]] = {
            v["key"]: v["payload"] for v in verticals
        }

    def validate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        errors = self._validator.validate(payload)
        return {"valid": len(errors) == 0, "errors": errors}

    def get_verticals(self) -> list[dict[str, Any]]:
        return self._verticals

    def get_suggested_payload(self, vertical_keys: list[str]) -> dict[str, Any]:
        """Deep-merge the payloads for the requested vertical keys.

        Raises:
            ValueError: if any key is not a recognised vertical.
        """
        unknown_keys = [k for k in vertical_keys if k not in self._vertical_index]
        if unknown_keys:
            raise ValueError(f"Unknown vertical keys: {', '.join(unknown_keys)}")

        merged: dict[str, Any] = {}
        for key in vertical_keys:
            merged = _deep_merge(merged, self._vertical_index[key])

        return {"payload": merged}
