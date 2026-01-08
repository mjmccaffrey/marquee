"""Marquee Lighted Sign Project - event"""

from dataclasses import dataclass, field
from heapq import heapify, heappop, heappush
import time
from typing import Callable, NoReturn

@dataclass(order=True, repr=False)
class Event:
    """Scheduled event."""
    due: float
    owner: object 
    action: Callable = field(compare=False)
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
        # print(f"Event {event} removed from queue.")
        return event

    def push(self, event: Event) -> None:
        """Add event to queue."""
        heappush(self._queue, event)
        # print(f"Event {event} added to queue.")

    def wait(
        self, 
        seconds: float | None, 
        wait_fn: Callable[[float | None], None | NoReturn],
    ):
        """Call wait_fn to wait seconds, or indefinitely if seconds is None.
           wait_fn calls a threading.Event.wait method or equivalent."""
        now: float
        remaining: float
        start: float
        end: float

        def next_event_or_wait() -> tuple[Event | None, float | None]:
            """Return the next event if it is due, 
               otherwise return seconds to wait."""
            if self._queue:
                event = self.peek()
                if event.due < now:
                    # print(f"Running {event} {now - event.due} late")
                    self.pop()
                    return event, 0
                elif seconds is None or event.due < end:
                    # print(f"Waiting for {event} or button push")
                    return None, event.due - now
                else:
                    print(f"Waiting for remaining {remaining} or button push; queue not empty")
                    return None, remaining
            else:
                if seconds is None:
                    print(f"Waiting for button push")
                    return None, None
                else:
                    print(f"Waiting for remaining {remaining} or button push; queue empty")
                    return None, remaining

        print(f"Wait {seconds}")
        start = time.time()
        while True:
            now = time.time()
            if seconds is not None:
                remaining = start + seconds - now
                end = now + remaining
                if now > end:
                    print(f"Exiting wait {now - end} late")
                    break
            event, duration = next_event_or_wait()
            if event is not None:
                event.action()
            else:
                wait_fn(duration)

