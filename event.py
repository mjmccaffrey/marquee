"""Marquee Lighted Sign Project - event"""

from dataclasses import dataclass, field
from heapq import heapify, heappop, heappush
from typing import Callable

@dataclass(order=True, repr=False)
class Event:
    """Scheduled event."""
    due: float
    owner: object 
    action: Callable
    name: str = ''

    def __repr__(self) -> str:
        return f"<{self}>"
    
    def __str__(self) -> str:
        return f"{self.name} {self.due}"

@dataclass
class PriorityQueue:
    """Priority event queue."""
    _queue: list[Event] = field(default_factory=list)

    def __len__(self) -> int:
        """Number of events in queue."""
        return len(self._queue)
    
    def bulk_add(self, new: list[Event]):
        """"""
        self._queue.extend(new)
        heapify(self._queue)
        print(f"{len(new)} events added to queue.")

    def delete_owned_by(self, owner: object) -> None:
        """Delete all events owned by owner."""
        self._queue = [event for event in self._queue if event.owner is not owner]
        heapify(self._queue)
        print(f"Events owned by {owner} deleted from queue.")

    def peek(self) -> Event:
        """Return next event without removing from queue."""
        assert self._queue, "Cannot peek into empty queue."
        return self._queue[0]

    def pop(self) -> Event:
        """Remove and return next event from queue."""
        event = heappop(self._queue)
        print(f"Event {event} removed from queue.")
        return event

    def push(self, event: Event) -> None:
        """Add event to queue."""
        heappush(self._queue, event)
        print(f"Event {event} added to queue.")

