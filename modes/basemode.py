"""Marquee Lighted Sign Project - basemode"""

from abc import ABC
from dataclasses import dataclass
from typing import Callable

from event import Event
from playerinterface import PlayerInterface
from .modeinterface import ModeInterface

@dataclass
class BaseMode(ModeInterface, ABC):
    """Base for both foreground and background modes."""
    player: PlayerInterface

    def schedule(self, action: Callable, due: float, name: str = '') -> None:
        """Schedule a new event."""
        self.player.event_queue.push(
            Event(
                action=action,
                due=due,
                owner=self,
                name=name,
            )
        )

