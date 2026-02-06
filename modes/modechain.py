"""Marquee Lighted Sign Project - modechain"""

from dataclasses import dataclass
from itertools import cycle

from devices.devices_misc import ButtonInterface
from .backgroundmode import BackgroundMode
from .mode_misc import BGModeEntry


@dataclass(kw_only=True)
class ModeChain(BackgroundMode):
    """Play repeating sequence of foreground modes."""
    sequence: list[tuple[str, int]]  # (mode_name, seconds)

    def __post_init__(self) -> None:
        """Initialize."""
        self.create_mode_sequence()
        self.mode_iter = cycle(self.mode_sequence)
        self.mode_on_deck = next(self.mode_iter)

    def create_mode_sequence(self) -> None:
        """Create mode sequence."""
        self.mode_sequence = [
            BGModeEntry(
                name,
                seconds,
                self.lookup_mode_index(name),
            )
            for name, seconds in self.sequence
        ]

    def execute(self):
        """Schedule next next mode. Change to next mode in sequence."""
        print(
            f"Next mode in sequence is "
            f"{self.mode_on_deck.name} for "
            f"{self.mode_on_deck.seconds} seconds."
        )
        self.schedule(
            action=self.execute,
            due=self.mode_on_deck.seconds,
        )
        new_mode = self.mode_on_deck.index
        self.mode_on_deck = next(self.mode_iter)
        self.change_mode(new_mode)
    
    def button_action(self, button: ButtonInterface) -> None:
        """Close the instance in response to any button press."""
        # self.player.delete_mode_instance(bg_index=self.index)
        # !!!!!!!!!!!!!!1

