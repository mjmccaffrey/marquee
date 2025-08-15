"""Marquee Lighted Sign Project - buttoninterface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

class ButtonInterface(ABC):
    """Button interface."""

    @classmethod
    @abstractmethod
    def reset(cls):
        """Prepare for a button press."""

    @classmethod
    @abstractmethod
    def wait(cls, seconds: float | None):
        """Wait until seconds have elapsed 
           or any button is pressed."""
    
    @abstractmethod
    def close(self):
        """Clean up."""

    @abstractmethod
    def button_pressed(self):
        """Callback for button press."""

    @abstractmethod
    def virtual_button_pressed(self):
        """Callback for virtual button press."""

@dataclass
class ButtonSet:
    """Every button."""
    body_back: ButtonInterface
    remote_a: ButtonInterface
    remote_b: ButtonInterface
    remote_c: ButtonInterface
    remote_d: ButtonInterface
