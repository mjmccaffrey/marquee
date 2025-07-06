"""Marquee Lighted Sign Project - button interface."""

from abc import ABC, abstractmethod

class ButtonInterface(ABC):
    """Button interface."""

    @classmethod
    @abstractmethod
    def reset(cls):
        """Prepare for a button press."""

    @classmethod
    @abstractmethod
    def wait(cls, seconds: float | None):
        """Wait until seconds have elapsed or any button is pressed."""
    
    @abstractmethod
    def close(self):
        """Clean up."""

    @abstractmethod
    def button_pressed(self):
        """Callback for button press."""

    @abstractmethod
    def virtual_button_pressed(self):
        """Callback for virtual button press."""
