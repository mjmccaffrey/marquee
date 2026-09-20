"""Marquee Lighted Sign Project - task"""

from collections.abc import Callable
from dataclasses import dataclass, field, replace
from heapq import heapify, heappop, heappush
import logging
import threading
import time
from typing import NoReturn
from typing_extensions import override

log = logging.getLogger('marquee.' + __name__)


@dataclass(order=True, frozen=True, repr=False)
class Task:
    """Scheduled task."""
    due: float
    owner: object 
    action: Callable = field(compare=False)
    name: str = ''

    @override
    def __repr__(self) -> str:
        return f"<{self}>"
    
    @override
    def __str__(self) -> str:
        return f"'{self.name}' {self.owner}"


@dataclass
class TaskSchedule:
    """Task schedule."""
    _schedule: list[Task] = field(default_factory=list)

    def __len__(self) -> int:
        """Number of tasks in schedule."""
        return len(self._schedule)

    @override
    def __repr__(self) -> str:
        return f"<{self}>"
    
    @override
    def __str__(self) -> str:
        return '\n'.join(
            str(e) for e in sorted(self._schedule)
        )
    
    def bulk_add(self, new: list[Task]):
        """Add a chunk of tasks to the schedule."""
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
        # log.info(f"Task {task} removed from schedule.")
        return task

    def push(self, task: Task) -> None:
        """Add task to schedule."""
        heappush(self._schedule, task)

    def delay_all(self, delta: float):
        """Push all scheduled tasks back by delta seconds."""
        self._schedule = [
            replace(task, due=task.due + delta)
            for task in self._schedule
        ]
        heapify(self._schedule)
        log.debug(f"{len(self._schedule)} tasks delayed by {delta} seconds.")

    def next_task_or_wait_duration(self) -> Task | float | None:
        """If the next task is due, return task.
           Else return seconds until the next task.
           Except if there are no more tasks, return None."""
        now = time.time()
        if self._schedule:
            task = self.peek()
            if task.due < now:
                # log.info(f"Running {task} {now - task.due} late")
                self.pop()
                return task
            else:
                log.info(f"Waiting for {task.due - now} or interrupt")
                return task.due - now
        else:
            log.info(f"Waiting for interrupt")
            return None


@dataclass
class SeqTask:
    """Sequential task."""
    action: Callable | None = None
    due: float = 0.0
    name: str | None = None

