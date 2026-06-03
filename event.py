"""Marquee Lighted Sign Project - event"""

from collections import defaultdict
from collections.abc import Callable
import logging

log = logging.getLogger('marquee.' + __name__)


class EventSystem:
    """Simple event / messaging system."""
    subscriptions: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, fn: Callable) -> None:
        """Associate a new callable with an event."""
        self.subscriptions[event].append(fn)

    def notify(self, event: str, **kwargs) -> None:
        """Execute callables associated with event."""
        if event not in self.subscriptions:
            raise RuntimeError(event)
        for callback in self.subscriptions[event]:
            callback(**kwargs)

