"""Marquee Lighted Sign Project - tools"""

from collections.abc import Sequence
from dataclasses import astuple, fields
import json
from pathlib import Path
from typing import cast

from devices.color import Color, ColorSets
from instruments import LightSet
from devices.hue import HueBridge
from device_defs import define_devices


def setup():
    global b, d, l, e, clicker, r, z, j, t, c
    devices = define_devices(1.0, 1.0)
    b, d, l, e, c, clicker, r, z, j, t = devices.astuple()


def ppp(p: Sequence) -> None:
    """Pretty print pattern p."""
    print(
        f"  {p[0]} {p[1]} {p[2]}\n"
        f"{p[11]}       {p[3]}\n"
        f"{p[10]}       {p[4]}\n"
        f"{p[9]}       {p[5]}\n"
        f"  {p[8]} {p[7]} {p[6]}\n"
    )


def get_color_set(hue: HueBridge, name: str):
    """"""
    hue._create_channels()
    return {
        name: tuple(
            (
                cast(Color, channel.color).x,
                cast(Color, channel.color).y,
                channel.brightness,
            )
            for channel in hue.channels
        )
    }


def merge_color_files(filepath: str) -> list:
    """"""
    result = []
    for file in Path().glob("color_sets/*.json"):
        print(f"{file=}")
        data = json.load(file.open())
        for set_name, data in cast(dict, data).items():
            result.append([set_name, file.stem, data])
    json.dump(result, open(filepath, 'wt'))
    return result


def view_each_color_set(l: LightSet, css: ColorSets):
    """"""
    for gname, csets in sorted(css.by_group_name.items()):
        for sname in sorted(s.name for s in csets):
            input(f"{gname} {sname}")
            cs = css.by_set_name[sname]
            l.set_channels(**cs.set_channels_kwargs(l.count))

def apply_color_set_fixes():
    """"""
    broken = json.load(open('color_sets/color_sets.json'))
    fixes = json.load(open('color_sets/color_fixes.json'))
    for k, v in fixes.items():
        gn, sn = k.split('.')
        bi = next(i for i, b in enumerate(broken) if b[0] == sn)
        broken[bi] = [sn, gn]
    json.dump(broken, open('color_sets/color_sets_fixed.json', 'w'))

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

