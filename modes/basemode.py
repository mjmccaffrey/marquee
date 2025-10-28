"""Marquee Lighted Sign Project - basemode"""

from abc import ABC
from dataclasses import dataclass

from event import Event
from .modeinterface import ModeInterface
from player import Player
from typing import Callable


@dataclass
class BaseMode(ModeInterface, ABC):
    """Base for foreground and background modes."""
    player: Player

    def __post_init__(self) -> None:
        """Copy resource attributes for convenience."""
        self.bells = self.player.bells
        self.buttons = self.player.buttons
        self.drums = self.player.drums
        self.lights = self.player.lights

    def schedule(self, action: Callable, due: float):
        """Create new event in the queue."""
        self.player.event_queue.push(
            Event(
                action=action,
                due=due,
                owner=self,
            )
        )
