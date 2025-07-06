"""Marquee Lighted Sign Project - mode interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

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
