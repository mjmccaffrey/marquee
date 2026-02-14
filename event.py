"""Marquee Lighted Sign Project - event"""

from collections import defaultdict
from collections.abc import Callable

type Callback = Callable[[],None]
type EventName = str

class EventSystem:
    """"""
    subscriptions: dict[EventName, list[Callback]] = defaultdict(list)

    def subscribe(self, event: EventName, fn: Callback) -> None:
        """"""
        self.subscriptions[event].append(fn)

    def notify(self, event: EventName) -> None:
        """"""
        if event not in self.subscriptions:
            raise ValueError("event")
        for callback in self.subscriptions[event]:
            callback()

