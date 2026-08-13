"""Marquee Lighted Sign Project - deviceset"""

from dataclasses import dataclass, fields
from devices.controlset import ControlSet
from devices.joystick import Joystick
from devices.tiltset import TiltSet
from instruments import (
    BellSet, Buzzer, ClickSet, DrumSet, LightSet, Ringer
)

@dataclass
class DeviceSet:
    # bells: BellSet
    controls: ControlSet
    drums: DrumSet
    lights: LightSet
    extra: LightSet
    combined: LightSet
    clicker: ClickSet
    ringer: Ringer
    buzzer: Buzzer
    joystick: Joystick
    # tilts: TiltSet

    def astuple(self) -> tuple[
        ControlSet, DrumSet, 
        LightSet, LightSet, LightSet, 
        ClickSet, Ringer, Buzzer, Joystick,
    ]:
        """Return devices as a tuple, since dataclasses.astuple
           will not work in this case."""
        return tuple(getattr(self, f.name) for f in fields(self))

