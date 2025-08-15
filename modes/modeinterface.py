"""Marquee Lighted Sign Project - modeinterface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from buttoninterface import ButtonInterface

@dataclass
class ModeInterface(ABC):
    """Mode interface."""
    player: Any
    name: str

    @abstractmethod
    def button_action(self, button: ButtonInterface):
        """Respond to button being pressed."""

    @abstractmethod
    def execute(self):
        """Play the mode."""
