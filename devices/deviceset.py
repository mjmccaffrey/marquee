"""Marquee Lighted Sign Project - deviceset"""

from typing import NotRequired, TypedDict

from devices.button import Button
from devices.joystick import Joystick
from devices.tiltset import TiltSet
from instruments import (
    BellSet, Buzzer, Clicker, DrumSet, LightSet, Ringer,
)


class DeviceSet(TypedDict):
    button_rear: Button
    button_corded_a: Button
    button_corded_b: Button
    button_game_start: NotRequired[Button]
    buzzer: NotRequired[Buzzer]
    clicker: Clicker
    drums: DrumSet
    joystick: NotRequired[Joystick]
    lights: LightSet
    ringer: NotRequired[Ringer]
    tilts: NotRequired[TiltSet]

