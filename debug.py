"""Marquee Lighted Sign Project - debug"""

from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial
import time

from lightset import LightSet
from setup_devices_hue import setup_devices


def setup():
    global bells, buttons, drums, primary, secondary

    bells, buttons, drums, primary, secondary = setup_devices(1.0, 1.0)


def ppp(p: Sequence) -> None:
    """Pretty print pattern p."""
    print(
        f"  {p[0]} {p[1]} {p[2]}\n"
        f"{p[11]}       {p[3]}\n"
        f"{p[10]}       {p[4]}\n"
        f"{p[9]}       {p[5]}\n"
        f"  {p[8]} {p[7]} {p[6]}\n"
    )

def light_states(lights: LightSet) -> None:
    """"""
    for i, c in enumerate(lights.channels):
        print(f"{i} {c.brightness} {c.color} {c.on}")


# @dataclass(kw_only=True)
# class BellTest(MusicMode):
#     """Test all bells."""

#     def __post_init__(self) -> None:
#         """Initialize."""

#     def execute(self) -> None:
#         """Perform bell test."""
#         for pitch in range(self.bells.pitch_levels):
#             due = 0.5 * pitch
#             self.schedule(
#                 action = partial(self.bells.play, {pitch}),
#                 due = due,
#                 name = f"BellTest play {pitch}",
#             )
#             self.schedule(
#                 action = partial(self.bells.release, {pitch}),
#                 due = due + self.bells.release_time,
#                 name = f"BellTest release {pitch}",
#             )

