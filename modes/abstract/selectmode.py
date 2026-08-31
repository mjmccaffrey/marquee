"""Marquee Lighted Sign Project - selectmode"""

from abc import ABC
from dataclasses import dataclass
import logging
from typing_extensions import override

from devices.device_schemas import ControlName
from .mode import Mode
from ..structural.mode_schemas import ModeDefinition
from ..structural.sequencemode import SequenceMode
from ..structural.sequences import rotate_build_flip

log = logging.getLogger('marquee.' + __name__)


@dataclass(kw_only=True)
class SelectMode(Mode, ABC):
    """Base for the selection modes."""

    def setup(
        self,
        lower: int,
        upper: int,
        previous: int,
    ) -> None:
        """Supports modes that allow the user to select a value."""
        self.lower: int = lower
        self.upper: int = upper
        self.previous: int = previous
        self.previous_desired: int | None = None
        self.desired: int = self.previous

    def update_desired(self, delta: int) -> int:
        """Update the current selection, wrapping within the bounds."""
        return self.wrap_value(self.lower, self.upper, self.desired, delta)

    @override
    def control_action(self, control: ControlName) -> None:
        """Respond to button being pressed.
           But first, delete the scheduled task which 
           would have finalized the selection."""
        self.tasks.delete_owned_by(self)
        b = ControlName
        match control:
            case b.BODY_BACK | b.CORDED_A | b.CORDED_B:
                self.desired = self.update_desired(+1)
            # case b.REMOTE_B:
            #     self.desired = self.update_desired(-1)
            case _:
                pass
        return None

    @override
    def execute(self) -> int | None:
        """Return user's final selection if made, otherwise 
           schedule next execute and return None."""
        log.info(
            f"SelectMode.execute {self.previous=} {self.previous_desired=} {self.desired=}"
        )
        if (    # The desired mode was not changed last go-around.
                self.desired != self.previous_desired 
                # If special mode, change mode immediately.
            and self.desired > 0 
        ):
            # Not last pass.
            # Show user what desired mode number is currently selected.
            log.info(f"Desired is now {self.desired}")
            # self.lights.set_relays(ALL_OFF, special=self.special)
            counter = self.create_mode_instance(
                mode_definition=ModeDefinition(
                    name='counter',
                    cls=SequenceMode,
                ),
                parent=self,
                kwargs=dict(
                    sequence=rotate_build_flip,
                    sequence_kwargs=dict(count=self.desired),
                    pre_delay=0.5,
                    delay=0.25, 
                    repeat=False,
                    special=self.special,
                ),
            )
            self.schedule(counter.execute)
            self.previous_desired = self.desired
            self.schedule(due=10.5 + self.desired * 0.4)
            return None
        else:
            # Last pass.
            # Time elapsed without a button being pressed.
            # Change the mode.
            log.info(f"Final selection is {self.desired}")
            return self.desired

