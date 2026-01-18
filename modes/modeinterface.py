# """Marquee Lighted Sign Project - modeinterface"""

# from abc import ABC, abstractmethod
# from dataclasses import dataclass
# from typing import Any

# from button_misc import ButtonInterface


# @dataclass
# class ModeInterface(ABC):
#     """Mode interface."""
#     player: Any
#     index: int
#     name: str

#     @abstractmethod
#     def button_action(self, button: ButtonInterface) -> int | None:
#         """Respond to button being pressed.
#            Return index of new mode, if any."""

#     @abstractmethod
#     def execute(self) -> None:
#         """Play the mode."""

