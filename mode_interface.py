"""Marquee Lighted Sign Project - mode_interfaces."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field

from button_interface import ButtonInterface
from definitions import AutoModeEntry
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
