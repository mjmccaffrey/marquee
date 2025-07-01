"""Marquee Lighted Sign Project - mode interface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from buttons import Button

class ModeInterface(ABC):
    """Mode abstract base."""
    def __init__(
            self, 
            player: Any,  # Player,
            name: str,
    ):
        self.player = player
        self.name = name

    @abstractmethod
    def button_action(self, button: Button):
        """"""        

    @abstractmethod
    def execute(self):
        """"""

@dataclass
class ModeConstructor:
    name: str
    mode_class: type[ModeInterface]
    kwargs: dict[str, Any]

@dataclass
class AutoModeChangeEntry:
    duration_seconds: int
    mode_index: int

class AutoModeChangeDue(Exception):
    """Automatic mode change due exception."""
