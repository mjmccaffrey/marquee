"""Marquee Lighted Sign Project - playerresources"""

import logging
from typing import Any, Protocol

from devices.device_schemas import DeviceSet
from event import EventSystem
from modes.structural.mode_schemas import ModeDefinition
from task import TaskSchedule

log = logging.getLogger('marquee.' + __name__)


class PlayerResources(Protocol):
    """Limited resources for use by mode."""

    # Read only
    devices: DeviceSet
    mode_ids: dict[str, int]
    modes: dict[int, ModeDefinition]

    # Read & write
    speed_factor: float
    events: EventSystem
    tasks: TaskSchedule

    def create_mode_instance(
        self,
        mode_index: int | None = None,
        mode_definition: ModeDefinition | None = None,
        kwargs: dict[str, Any] = {},
        parent: object | None = None,  # BaseMode
    ) -> object: ...  # BaseMode

    def delete_mode_instance(
        self,
        mode_index: int | None = None,
    ) -> None: ...

