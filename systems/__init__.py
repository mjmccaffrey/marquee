"""Marquee Lighted Sign Project - systems __init__"""

from dataclasses import dataclass
from enum import StrEnum, auto
from typing import cast

from schemas import LightConfig, SetupDevices
import systems.devices_marquee as marquee
import systems.devices_edwards as edwards


@dataclass
class System:
    """System definition."""
    setup_devices: SetupDevices
    light_config: LightConfig


class SystemName(StrEnum):
    """System names."""
    EDWARDS = auto()
    MARQUEE = auto()


systems: dict[SystemName, System] = {
    SystemName.EDWARDS: System(
        setup_devices=edwards.setup_devices, 
        light_config=edwards.light_config,
    ),
    SystemName.MARQUEE: System(
        setup_devices=marquee.setup_devices, 
        light_config=marquee.light_config,
    ),
}

