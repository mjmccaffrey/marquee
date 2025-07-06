"""Marquee Lighted Sign Project - mode interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Type

from button_interface import ButtonInterface
from player_interface import PlayerInterface

@dataclass
class ModeInterface(ABC):
    """Mode abstract base."""
    player: PlayerInterface
    name: str

    @abstractmethod
    def button_action(self, button: ButtonInterface):
        """"""        

    @abstractmethod
    def execute(self):
        """"""

@dataclass
class ModeConstructor:
    name: str
    mode_class: Type
    kwargs: dict[str, Any]

@dataclass
class AutoModeChangeEntry:
    duration_seconds: int
    mode_index: int

class AutoModeChangeDue(Exception):
    """Automatic mode change due exception."""
