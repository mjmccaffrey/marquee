"""Marquee Lighted Sign Project - buttonsets"""

from dataclasses import dataclass
from buttons import Button

@dataclass
class ButtonSet:
    """Every button."""
    body_back: Button
    remote_a: Button
    remote_b: Button
    remote_c: Button
    remote_d: Button
