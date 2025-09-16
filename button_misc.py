"""Marquee Lighted Sign Project - buttonprotocol"""

from dataclasses import dataclass
from typing import Protocol

class ButtonProtocol(Protocol):
    """Button protocol."""

    @classmethod
    def reset(cls):
        """Prepare for a button press."""
        ...

    @classmethod
    def wait(cls, seconds: float | None):
        """Wait until seconds have elapsed or any button is pressed."""
        ...
    
    def close(self):
        """Clean up."""
        ...

    def button_pressed(self):
        """Callback for button press."""
        ...

    def virtual_button_pressed(self):
        """Callback for virtual button press."""
        ...

@dataclass
class ButtonSet:
    """Every button."""
    body_back: ButtonProtocol
    remote_a: ButtonProtocol
    remote_b: ButtonProtocol
    remote_c: ButtonProtocol
    remote_d: ButtonProtocol
