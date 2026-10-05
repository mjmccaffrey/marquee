"""Marquee Lighted Sign Project - playerresources"""

import logging
from typing import Protocol

from devices.deviceset import DeviceSet
from event import EventSystem
from schemas import BaseModeInterface, Interrupt, ModeDefinition
from task import TaskSchedule

log = logging.getLogger('marquee.' + __name__)


class PlayerResources(Protocol):
    """Limited resources for use by mode instances."""

    # Read only
    devices: DeviceSet
    mode_ids: dict[str, int]
    modes: dict[int, ModeDefinition]
    active_modes: dict[int, BaseModeInterface]

    # Read & write
    speed_factor: float
    events: EventSystem
    tasks: TaskSchedule

    def create_active_mode(
        self,
        mode_index: int | None = None,
        mode_definition: ModeDefinition | None = None,
        parent: BaseModeInterface | None = None,
    ) -> BaseModeInterface: ...

    def delete_active_mode(self, mode_index: int) -> None: ...
    
    def execute_interrupt(self, interrupt: Interrupt) -> None: ...

