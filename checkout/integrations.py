"""Self-registering integration registry.

Decorate any checkout route with ``@register_integration(...)`` and it will
automatically appear on the integration-selection page.  No other file needs
to be edited.
"""

_REGISTRY = []


def register_integration(name, description, note=None, order=100):
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
    def decorator(func):
        _REGISTRY.append({
            "name": name,
            "description": description,
            "note": note,
            "endpoint": func.__name__,
            "order": order,
        })
        return func
    return decorator


def get_integrations():
    """Return registered integrations sorted by ``order``."""
    return sorted(_REGISTRY, key=lambda i: i["order"])
