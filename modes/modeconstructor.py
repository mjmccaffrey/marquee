"""Marquee Lighted Sign Project - modeconstructor"""

from dataclasses import dataclass
from typing import Any, Type

@dataclass
class ModeConstructor:
    name: str
    mode_class: Type
    kwargs: dict[str, Any]
