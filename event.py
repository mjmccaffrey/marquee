"""Marquee Lighted Sign Project - event"""

from collections import defaultdict
from collections.abc import Callable


class EventSystem:
    """"""
    subscriptions: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, fn: Callable) -> None:
        """"""
        self.subscriptions[event].append(fn)

    def notify(self, event: str, **kwargs) -> None:
        """"""
        if event not in self.subscriptions:
            raise ValueError("event")
        for callback in self.subscriptions[event]:
            callback(**kwargs)

