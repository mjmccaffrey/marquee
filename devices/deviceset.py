"""Marquee Lighted Sign Project - deviceset"""

from dataclasses import dataclass
from devices.buttonset import ButtonSet
from devices.joystick import Joystick
from instruments import BellSet, ClickSet, DrumSet, LightSet, RingerBell

@dataclass
class DeviceSet:
    # bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    aux: LightSet | None
    clicker: ClickSet
    ringer: RingerBell
    joystick: Joystick

