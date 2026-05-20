"""Core validation logic.

Fetches the Adyen Checkout OpenAPI spec from GitHub and validates a
/payments payload against the PaymentRequest schema using jsonschema.
"""

from __future__ import annotations

import threading
from typing import Any

import requests
from jsonschema import Draft4Validator, ValidationError

# ---------------------------------------------------------------------------
# OpenAPI spec fetching
# ---------------------------------------------------------------------------

_SPEC_URL = (
    "https://raw.githubusercontent.com/Adyen/adyen-openapi"
    "/main/json/CheckoutService-v71.json"
)

_spec_cache: dict[str, Any] | None = None
_spec_lock = threading.Lock()


def _fetch_spec() -> dict[str, Any]:
    """Download and cache the Adyen Checkout OpenAPI spec."""
    global _spec_cache
    if _spec_cache is not None:
        return _spec_cache
    with _spec_lock:
        if _spec_cache is not None:
            return _spec_cache
        response = requests.get(_SPEC_URL, timeout=15)
        response.raise_for_status()
        _spec_cache = response.json()
        return _spec_cache


def _resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    """Resolve a $ref pointer like '#/components/schemas/Foo'."""
    parts = ref.lstrip("#/").split("/")
    node = spec
    for part in parts:
        node = node[part]
    return node


def _build_schema(spec: dict[str, Any], schema_name: str) -> dict[str, Any]:
    """Build a fully self-contained JSON Schema for *schema_name*.

    The OpenAPI spec uses ``$ref`` pointers into ``components/schemas``.
    jsonschema's Draft4Validator does not resolve OpenAPI-style refs
    out of the box, so we inline the definitions using a JSON Schema
    ``definitions`` block and rewrite refs accordingly.
    """
    components = spec.get("components", {}).get("schemas", {})

    # Collect all schemas as definitions and rewrite $ref pointers
    definitions: dict[str, Any] = {}
    for name, body in components.items():
        definitions[name] = _rewrite_refs(body)

    root = dict(definitions[schema_name])
    root["definitions"] = definitions
    return root


def _rewrite_refs(node: Any) -> Any:
    """Recursively rewrite ``#/components/schemas/X`` → ``#/definitions/X``."""
    if isinstance(node, dict):
        if "$ref" in node:
            ref = node["$ref"]
            if ref.startswith("#/components/schemas/"):
                name = ref.split("/")[-1]
                return {"$ref": f"#/definitions/{name}"}
            return node
        return {k: _rewrite_refs(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_rewrite_refs(item) for item in node]
    return node


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_payments_payload(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Validate *payload* against the PaymentRequest schema.

    Returns a list of error dicts, each with ``path``, ``message``, and
    ``schema_path`` keys.  An empty list means the payload is valid.
    """
    spec = _fetch_spec()
    schema = _build_schema(spec, "PaymentRequest")

    validator = Draft4Validator(schema)
    errors: list[dict[str, str]] = []
    for error in sorted(validator.iter_errors(payload), key=lambda e: list(e.path)):
        errors.append({
            "field": ".".join(str(p) for p in error.absolute_path) or "(root)",
            "error": error.message,
            "rule": _humanize_rule(error),
        })
    return errors


def _humanize_rule(error: ValidationError) -> str:
    """Convert a jsonschema error into a short, human-readable rule label."""
    validator_name = error.validator

    if validator_name == "required":
        return "required field"
    if validator_name == "type":
        expected = error.schema.get("type", "unknown")
        return f"expected type: {expected}"
    if validator_name == "enum":
        allowed = error.schema.get("enum", [])
        return f"allowed values: {', '.join(str(v) for v in allowed)}"
    if validator_name == "minLength":
        return f"min length: {error.schema.get('minLength', '?')}"
    if validator_name == "maxLength":
        return f"max length: {error.schema.get('maxLength', '?')}"
    if validator_name == "pattern":
        return f"must match pattern: {error.schema.get('pattern', '?')}"
    if validator_name == "minimum":
        return f"minimum value: {error.schema.get('minimum', '?')}"
    if validator_name == "maximum":
        return f"maximum value: {error.schema.get('maximum', '?')}"
    if validator_name == "additionalProperties":
        return "unexpected field"
    if validator_name == "oneOf":
        return "must match exactly one schema"
    if validator_name == "anyOf":
        return "must match at least one schema"

    return validator_name
