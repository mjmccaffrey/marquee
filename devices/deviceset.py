"""Marquee Lighted Sign Project - deviceset"""

from typing import TypedDict

from devices.button import Button
from devices.joystick import Joystick
from devices.tiltset import TiltSet
from instruments import (
    BellSet, Buzzer, Clicker, DrumSet, LightSet, Ringer,
)


class DeviceSet(TypedDict, total=False):
    button_rear: Button
    button_corded_a: Button
    button_corded_b: Button
    button_game_start: Button
    buzzer: Buzzer
    clicker: Clicker
    drums: DrumSet
    joystick: Joystick
    lights: LightSet
    ringer: Ringer
    tilts: TiltSet

