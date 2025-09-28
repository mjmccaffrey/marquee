"""Marquee Lighted Sign Project - modeinterface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from button_misc import ButtonProtocol


@dataclass
class ModeInterface(ABC):
    """Mode interface."""
    player: Any
    name: str

    @abstractmethod
    def button_action(self, button: ButtonProtocol) -> None:
        """Respond to button being pressed."""

    @abstractmethod
    def execute(self) -> None:
        """Play the mode."""

