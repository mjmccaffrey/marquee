"""Marquee Lighted Sign Project - task"""

from collections.abc import Callable
from dataclasses import dataclass, field
from heapq import heapify, heappop, heappush
import logging
import time
from typing import NoReturn

log = logging.getLogger('marquee.' + __name__)


@dataclass(order=True, repr=False)
class Task:
    """Scheduled task."""
    due: float
    owner: object 
    action: Callable = field(compare=False)
    name: str = ''

    def __repr__(self) -> str:
        return f"<{self}>"
    
    def __str__(self) -> str:
        return f"'{self.name}' {self.owner}"

@dataclass
class TaskSchedule:
    """Task schedule."""
    _schedule: list[Task] = field(default_factory=list)

    def __len__(self) -> int:
        """Number of tasks in schedule."""
        return len(self._schedule)

    def __repr__(self) -> str:
        return f"<{self}>"
    
    def __str__(self) -> str:
        return '\n'.join(
            str(e) for e in sorted(self._schedule)
        )
    
    def bulk_add(self, new: list[Task]):
        """"""
        self._schedule.extend(new)
        heapify(self._schedule)
        log.debug(f"{len(new)} tasks added to schedule.")

    def delete_owned_by(self, owner: object) -> None:
        """Delete all tasks owned by owner."""
        self._schedule = [task for task in self._schedule if task.owner is not owner]
        heapify(self._schedule)
        log.debug(f"Tasks owned by {owner} deleted from schedule.")

    def peek(self) -> Task:
        """Return next task without removing from schedule."""
        assert self._schedule, "Cannot peek into empty schedule."
        return self._schedule[0]

    def pop(self) -> Task:
        """Remove and return next task from schedule."""
        task = heappop(self._schedule)
        # log.debug(f"Task {task} removed from schedule.")
        return task

    def push(self, task: Task) -> None:
        """Add task to schedule."""
        heappush(self._schedule, task)
        # log.debug(self)
        # log.debug('')
        # log.debug(f"schedule length: {len(self._schedule)}")
        # log.debug(f"Task {task} added to schedule.")

    def wait(
        self, 
        seconds: float | None, 
        wait_fn: Callable[[float | None], None | NoReturn],
    ):
        """Call wait_fn to wait seconds, or indefinitely if seconds is None.
           wait_fn calls a threading.Task.wait method or equivalent."""
        now: float
        remaining: float
        start: float
        end: float

        def next_task_or_wait() -> tuple[Task | None, float | None]:
            """Return the next task if it is due, 
               otherwise return seconds to wait."""
            if self._schedule:
                task = self.peek()
                if task.due < now:
                    log.debug(f"Running {task} {now - task.due} late")
                    self.pop()
                    return task, 0
                elif seconds is None or task.due < end:
                    log.debug(f"Waiting for {task} or button push")
                    log.debug(f"Waiting for {task.due - now} or button push")
                    return None, task.due - now
                else:
                    log.debug(f"Waiting for remaining {remaining} or button push; schedule not empty")
                    return None, remaining
            else:
                if seconds is None:
                    log.debug(f"Waiting for button push")
                    return None, None
                else:
                    log.debug(f"Waiting for remaining {remaining} or button push; schedule empty")
                    return None, remaining

        log.debug(f"Waiting {seconds=}")
        start = time.time()
        while True:
            now = time.time()
            if seconds is not None:
                remaining = start + seconds - now
                end = now + remaining
                if now > end:
                    log.debug(f"Exiting wait {now - end} late")
                    break
            task, duration = next_task_or_wait()
            if task is not None:
                print('!!!!!!!!!!!!!', task)
                task.action()
            else:
                wait_fn(duration)

