"""Marquee Lighted Sign Project - mode interface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


from buttons import Button
from players import Player

class ModeInterface(ABC):
    """Mode abstract base."""
    def __init__(
            self, 
            player: Player,
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
