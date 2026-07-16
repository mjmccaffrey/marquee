"""Marquee Lighted Sign Project - deviceset"""

from dataclasses import dataclass, fields
from devices.buttonset import ButtonSet
from devices.joystick import Joystick
from devices.tiltset import TiltSet
from instruments import BellSet, ClickSet, DrumSet, LightSet, Ringer

@dataclass
class DeviceSet:
    # bells: BellSet
    buttons: ButtonSet
    drums: DrumSet
    lights: LightSet
    extra: LightSet | None
    clicker: ClickSet
    ringer: Ringer
    joystick: Joystick
    tilts: TiltSet

    def astuple(self) -> tuple[
        ButtonSet, DrumSet, LightSet, LightSet | None, 
        ClickSet, Ringer, Joystick, TiltSet,
    ]:
        """Return devices as a tuple, since dataclasses.astuple
           will not work in this case."""
        return tuple(getattr(self, f.name) for f in fields(self))

