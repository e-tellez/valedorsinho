"""Self-registering integration registry.

Decorate any checkout route with ``@register_integration(...)`` and it will
automatically appear on the integration-selection page.  No other file needs
to be edited.
"""

from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

_REGISTRY: list[dict[str, Any]] = []


def register_integration(
    name: str,
    description: str,
    note: str | None = None,
    order: int = 100,
) -> Callable[[F], F]:
    """Decorator that registers a Flask view function as a selectable integration.

    Parameters
    ----------
    name : str
        Display name shown on the integration card.
    description : str
        Short description shown below the name.
    note : str, optional
        Extra note rendered above the description (e.g. a WIP warning).
    order : int
        Controls display order — lower numbers appear first.
    """
    def decorator(func: F) -> F:
        _REGISTRY.append({
            "name": name,
            "description": description,
            "note": note,
            "endpoint": func.__name__,
            "order": order,
        })
        return func
    return decorator


def get_integrations() -> list[dict[str, Any]]:
    """Return registered integrations sorted by ``order``."""
    return sorted(_REGISTRY, key=lambda i: i["order"])
