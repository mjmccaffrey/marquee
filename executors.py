"""Marquee Lighted Sign Project - executors"""

from collections.abc import Callable
from signal import SIGUSR1  # type: ignore

from buttons import Button
from dimmers import ShellyDimmer, ShellyProDimmer2PM, RelayOverride, TRANSITION_DEFAULT
from gpiozero import Button as _Button  # type: ignore
from modes import *
from mode_defs import *
from players import Player
from relays import NumatoUSBRelayModule, NumatoRelayModuleRL160001 as NumatoRL160001
from sequence_defs import *
from signs import (
    ALL_RELAYS, ALL_OFF,
    EXTRA_COUNT, Sign,
)
DIMMER_ADDRESSES = [
    '192.168.51.111',
    '192.168.51.112',
    '192.168.51.113',
    '192.168.51.114',
    '192.168.51.115',
]
#   '192.168.51.116',

def create_sign() -> Sign:
    """Creates and returns a Sign object and all associated device objects."""
    dimmers: list[ShellyDimmer] = [
        ShellyProDimmer2PM(index, address)
        for index, address in enumerate(DIMMER_ADDRESSES)
    ]
    relaymodule: NumatoUSBRelayModule = NumatoRL160001("/dev/ttyACM0", ALL_RELAYS)
    buttons = [
        Button('sign_back', _Button(pin=17, bounce_time=0.10), SIGUSR1),
        Button('remote_a', _Button(pin=18, pull_up=False, bounce_time=0.10)),
        Button('remote_b', _Button(pin=23, pull_up=False, bounce_time=0.10)),
        Button('remote_c', _Button(pin=24, pull_up=False, bounce_time=0.10)),
        Button('remote_d', _Button(pin=25, pull_up=False, bounce_time=0.10)),
    ]
    return Sign(
        dimmers=dimmers,
        relaymodule=relaymodule,
        buttons=buttons,
    )

class Executor():
    """Executes patterns and commands specified on the command line.
       Registers all of the play modes, and if specified on the command line,
       creates and turns control over to a Player object."""

    def __init__(
            self, 
            create_sign: Callable[[], Sign],
            create_player: Callable[[dict[int, Mode], Sign, float], Player],
        ):
        """"""
        self.create_sign = create_sign
        self.create_player = create_player
        self.mode_ids: dict[str, int] = {}
        self.mode_menu: list[tuple[int, str]] = []
        self.modes: dict[int, Mode] = {}
        self.register_mode_ids()
        self.commands: dict[str, Callable] = {
            'calibrate_dimmers': self.command_calibrate_dimmers,
            'configure_dimmers': self.command_configure_dimmers,
            'off': self.command_off,
        }

    def close(self):
        """Close dependencies."""
        self.player.close()
        self.sign.close()

    def command_calibrate_dimmers(self):
        """Calibrate dimmers."""
        ShellyDimmer.calibrate_all()

    def command_configure_dimmers(self):
        """Configure dimmers."""
        ShellyDimmer.configure_all()

    def command_off(self):
        """Turn off all relays and potentially other devices."""
        self.sign.set_lights(ALL_OFF, '0' * EXTRA_COUNT)
        print("Marquee hardware is now partially shut down.")
        print()

    def add_mode_ids(
            self, 
            index: int, 
            name: str, 
        ):
        """Register the mode index and name."""
        assert (str(index) not in self.mode_ids
            and name not in self.mode_ids
        ), "Duplicate mode index or name"
        assert all(
            str(k) in self.mode_ids for k in range(1, index)
        ), "Non-sequential mode index"
        self.mode_menu.append((index, name))
        self.mode_ids[str(index)] = index
        self.mode_ids[name] = index

    def add_mode(
            self, 
            index: int, 
            mode: Mode,
            hidden: bool = False,
    ):
        """Register the Mode object."""
        assert hidden or (
                self.mode_ids.get(str(index)) == index
            and self.mode_ids.get(mode.name) == index
        ), "Mode index and / or name do not match registered IDs"
        self.modes[index] = mode

    def add_mode_def(
            self, 
            index: int, 
            name: str, 
            function: Callable,
            preset_dimmers: bool = False,
            preset_relays: bool = False,
        ):
        """Create a Mode object from a function and parameters, and register it."""
        self.add_mode(
            index, 
            PlayMode(self.player, name, function, preset_dimmers, preset_relays),
        )

    def add_sequence_mode_def(
            self,
            index: int, 
            name: str, 
            sequence: Callable,
            pace: tuple[float, ...] | float | None = None,
            override: RelayOverride | None = None,
        ):
        """Create a Mode object from a sequence and parameters, and register it."""
        if override is not None:
            default_trans = (
                pace if isinstance(pace, float) else
                TRANSITION_DEFAULT
            )
            if override.transition_off is None:
                override.transition_off = default_trans
            if override.transition_on is None:
                override.transition_on = default_trans
        function = self.player.sequence_player_func(
            sequence, pace, override
        )
        self.add_mode_def(
            index=index,
            name=name,
            function=function,
            preset_dimmers=(override is None),
            preset_relays=(override is not None),
        )

    def execute(
            self, 
            command: str | None = None, 
            mode_index: int | None = None, 
            speed_factor: float | None = None,
            light_pattern: str | None = None, 
            brightness_pattern: str | None = None,
        ):
        """Effects the command-line specified command, mode or pattern(s)."""
        self.sign = self.create_sign()
        if command is not None:
            self.execute_command(command)
        elif mode_index is not None:
            assert speed_factor is not None
            self.execute_mode(mode_index, speed_factor)
        else:
            self.execute_pattern(light_pattern, brightness_pattern)

    def execute_command(self, command: str):
        """Effects the command-line specified command."""
        self.commands[command]()

    def execute_mode(self, mode_index: int, speed_factor: float):
        """Effects the command-line specified mode."""
        self.player = self.create_player(self.modes, self.sign, speed_factor)
        self.register_mode_functions()
        self.player.execute(mode_index)

    def execute_pattern(self, light_pattern: str | None, brightness_pattern: str | None):
        """Effects the command-line specified pattern(s)."""
        if brightness_pattern is not None:
            print(f"Setting dimmers {brightness_pattern}")
            self.sign.set_dimmers(brightness_pattern)
            Button.wait(TRANSITION_DEFAULT)
        if light_pattern is not None:
            print(f"Setting lights {light_pattern}")
            self.sign.set_lights(light_pattern)

    def register_mode_ids(self):
        """Register all mode indexes and names, for command-line processing."""
        self.add_mode_ids(1, "all_on")
        self.add_mode_ids(2, "all_off")
        self.add_mode_ids(3, "even_on")
        self.add_mode_ids(4, "even_off")
        self.add_mode_ids(5, "blink_all")
        self.add_mode_ids(6, "blink_alternate")
        self.add_mode_ids(7, "rotate")
        self.add_mode_ids(8, "random_flip")
        self.add_mode_ids(9, "demo")
        self.add_mode_ids(10, "blink_alternate_fade")
        self.add_mode_ids(11, "random_flip_fade")
        self.add_mode_ids(12, "blink_all_fade_seq")
        self.add_mode_ids(13, "blink_all_fade_con")
        self.add_mode_ids(14, "blink_all_fade_fast")
        self.add_mode_ids(15, "blink_all_fade_slowwww")
        self.add_mode_ids(16, "blink_all_fade_stealth")
        self.add_mode_ids(17, "corner_rotate_fade")
        self.add_mode_ids(18, "rotate_slight_fade")
        self.add_mode_ids(19, "even_odd_fade")
        self.add_mode_ids(20, "random_fade")
        self.add_mode_ids(21, "random_fade_steady")
        self.add_mode_ids(22, "build_brightness_equal")
        self.add_mode_ids(23, "build_brightness_unequal")
        self.add_mode_ids(24, "rotate_reversible_1")
        self.add_mode_ids(25, "rotate_reversible_2")

    def register_mode_functions(self):
        """Register all operating modes."""
        player = self.player
        sign = self.player.sign
        self.add_mode(0,
            SelectMode(player, "selection"),
            hidden=True,
        )
        self.add_sequence_mode_def(1, "all_on", seq_all_on)
        self.add_sequence_mode_def(2, "all_off", seq_all_off)
        self.add_sequence_mode_def(3, "even_on", seq_even_on)
        self.add_sequence_mode_def(4, "even_off", seq_even_off)
        self.add_sequence_mode_def(5, "blink_all", 
            seq_blink_all, pace=1,
        )
        self.add_sequence_mode_def(6, "blink_alternate", 
            seq_blink_alternate, pace=1, 
        )
        self.add_sequence_mode_def(7, "rotate",
            lambda: seq_rotate("1100000000"), pace=0.5,
        )
        self.add_sequence_mode_def(8, "random_flip",
            lambda: seq_random_flip(sign.light_pattern), pace=0.5,
        )
        self.add_sequence_mode_def(9, "demo",
            lambda: seq_random_flip(sign.light_pattern), pace=0.5,
        )
        self.add_sequence_mode_def(10, "blink_alternate_fade",
            seq_blink_alternate, pace=4, 
            override=RelayOverride(
                transition_on=1.0,
                transition_off=3.0,
            )
        )
        self.add_sequence_mode_def(11, "random_flip_fade",
            lambda: seq_random_flip(sign.light_pattern), pace=2.0,
            override=RelayOverride(),
        )
        self.add_sequence_mode_def(12, "blink_all_fade_seq",
            seq_blink_all, pace=1,
            override=RelayOverride(
                concurrent=False,
                transition_on=0.5,
                transition_off=0.5,
            )
        )
        self.add_sequence_mode_def(13, "blink_all_fade_con", 
            seq_blink_all, pace=1,
            override=RelayOverride(
                concurrent=True,
                transition_on=0.5,
                transition_off=0.5,
            )
        )
        self.add_sequence_mode_def(14, "blink_all_fade_fast", 
            seq_blink_all, pace=0.5,
            override=RelayOverride()
        )
        self.add_sequence_mode_def(15, "blink_all_fade_slowwww", 
            seq_blink_all, pace=10,
            override=RelayOverride(
                brightness_on=100,
                brightness_off=10,
            )
        )
        self.add_sequence_mode_def(16, "blink_all_fade_stealth", 
            seq_blink_all, pace=(1, 60),
            override=RelayOverride(
                transition_on=2,
                transition_off=2,
            )
        )
        self.add_sequence_mode_def(17, "corner_rotate_fade", 
            seq_opposite_corner_pairs, pace=5,
            override=RelayOverride(
                concurrent=True,
                brightness_on = 90,
                brightness_off = 10,
            )
        )
        self.add_sequence_mode_def(18, "rotate_slight_fade",
            seq_rotate, pace=0.5,
            override=RelayOverride(
                concurrent=False,
                brightness_on = 100,
                brightness_off = 30,
            )
        )
        self.add_mode_def(19, "even_odd_fade", 
            lambda: mode_even_odd_fade(player))
        self.add_mode_def(20, "random_fade", 
            lambda: mode_random_fade(player))
        self.add_mode_def(21, "random_fade_steady", 
            lambda: mode_random_fade(player))
        self.add_mode_def(22, "build_brightness_equal", 
            lambda: build_brightness(player, True))
        self.add_mode_def(23, "build_brightness_unequal", 
            lambda: build_brightness(player, False))
        self.add_mode(24,
            RotateReversible(self.player, "rotate_reversible_1", 
                "1" + "0" * (LIGHT_COUNT - 1), 0.5,
            )
        )
        self.add_mode(25,
            RotateReversible(self.player, "rotate_reversible_2", 
                "0" + "1" * (LIGHT_COUNT - 1), 0.5,
            )
        )
