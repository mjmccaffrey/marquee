"""Marquee Lighted Sign Project - playerinterface"""

from typing import Any, Protocol

# from modes.backgroundmode import BackgroundMode
# from modes.foregroundmode import ForegroundMode


class ChangeMode(Exception):
    """Change mode exception."""

class CreateModeInstance(Protocol):
    """"""
    def __call__(
        self,
        mode_index: int,
        kwargs: dict[str, Any] = {},
        parent: object | None = None,  # BaseMode
    ) -> object:  # BackgroundMode | ForegroundMode:
        ...

