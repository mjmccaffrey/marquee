"""Marquee Lighted Sign Project - buttonsets"""

from dataclasses import dataclass
from button_interface import ButtonInterface

@dataclass
class ButtonSet:
    """Every button."""
    body_back: ButtonInterface
    remote_a: ButtonInterface
    remote_b: ButtonInterface
    remote_c: ButtonInterface
    remote_d: ButtonInterface
