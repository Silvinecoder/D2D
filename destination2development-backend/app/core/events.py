from __future__ import annotations

from collections import defaultdict
from typing import Callable

_handlers: dict[str, list[Callable]] = defaultdict(list)


def subscribe(event_name: str):
    """Decorator: register a function to run when `event_name` is published."""

    def decorator(fn: Callable) -> Callable:
        _handlers[event_name].append(fn)
        return fn

    return decorator


def publish(event_name: str, **payload) -> None:
    """Call every handler registered for `event_name`, in order."""

    for handler in _handlers[event_name]:
        handler(**payload)
