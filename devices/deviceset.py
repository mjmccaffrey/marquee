"""Marquee Lighted Sign Project - deviceset"""

from dataclasses import dataclass, fields
from devices.buttonset import ButtonSet
from devices.joystick import Joystick
from instruments import BellSet, ClickSet, DrumSet, LightSet, RingerBell

@dataclass
class DeviceSet:
    # bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    extra: LightSet | None
    clicker: ClickSet
    ringer: RingerBell
    joystick: Joystick

    def astuple(self) -> tuple[
        ButtonSet, DrumSet, LightSet, LightSet | None, 
        ClickSet, RingerBell, Joystick
    ]:
        """"""
        return tuple(getattr(self, f.name) for f in fields(self))

