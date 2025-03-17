""""""

from collections.abc import Callable
from signal import SIGUSR1  # type: ignore

from buttons import Button
from dimmers import ShellyDimmer, ShellyProDimmer2PM, RelayOverride, TRANSITION_DEFAULT
from gpiozero import Button as _Button  # type: ignore
from modes import *
from players import Player
from relays import NumatoRL160001
from sequences import *
from signs import (
    ALL_RELAYS,
    ALL_HIGH, ALL_OFF, ALL_ON,
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
    """"""
    dimmers: list[ShellyDimmer] = [
        ShellyProDimmer2PM(index, address)
        for index, address in enumerate(DIMMER_ADDRESSES)
    ]
    relaymodule: NumatoRL160001 = NumatoRL160001("/dev/ttyACM0", ALL_RELAYS)
    buttons = [
        Button('body_mode_select', _Button(pin=17, bounce_time=0.10), SIGUSR1),
        Button('remote_mode_select', _Button(pin=18, pull_up=False, bounce_time=0.10)),  # A
        Button('remote_mode_up', _Button(pin=23, pull_up=False, bounce_time=0.10)),  # B
        Button('remote_demo_mode', _Button(pin=24, pull_up=False, bounce_time=0.10)),  # C
        Button('remote_mode_down', _Button(pin=25, pull_up=False, bounce_time=0.10)),  # D
    ]
    return Sign(
        dimmers=dimmers,
        relaymodule=relaymodule,
        buttons=buttons,
    )

class Executor():
    """"""

    def __init__(self):
        """"""
        self.mode_ids: dict[str, int] = {}
        self.modes: dict[int, Mode] = {}
        self.register_mode_ids()
        self.commands: dict[str, Callable] = {
            'calibrate_dimmers': self.command_calibrate_dimmers,
            'configure_dimmers': self.command_configure_dimmers,
            'off': self.command_off,
        }

    def close(self):
        """Close."""
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
        print("Marquee is now partially shut down.")
        print()

    def add_mode_ids(
            self, 
            index: int, 
            name: str, 
        ):
        """Register the mode, identified by index and name."""
        #assert (
        #        index not in self.modes
        #    and str(index) not in self.mode_ids 
        #    and name not in self.mode_ids 
        #), "Duplicate mode index or name"
        #assert all(
        #    k in self.modes for k in range(1, index)
        #), "Non-sequential mode index"
        self.mode_ids[str(index)] = index
        self.mode_ids[name] = index
        self.modes[index] = Mode(index, name, None)

    def add_mode_func(
            self, 
            index: int, 
            name: str, 
            function: Callable,
        ):
        self.modes[index] = Mode(index, name, function)
            
    def add_sequence_mode_func(
            self,
            index: int, 
            name: str, 
            sequence: Callable,
            pace: tuple[float, ...] | float | None = None,
            override: RelayOverride | None = None,
        ):
        """"""

        def sequence_doer():
            # If using only dimmers, turn relays on, and vice versa
            if override is not None:
                self.sign.set_lights(ALL_ON)
            else:
                self.sign.set_dimmers(ALL_HIGH)
            while True:
                self.player.do_sequence(sequence,
                    pace=pace,
                    override=override,
                )

        if override is not None:
            default_trans = (
                pace if isinstance(pace, float) else
                TRANSITION_DEFAULT
            )
            if override.transition_off is None:
                override.transition_off = default_trans
            if override.transition_on is None:
                override.transition_on = default_trans
        self.add_mode_func(
            index=index,
            name=name,
            function=sequence_doer
        )

    def execute(
            self, 
            command: str | None = None, 
            mode_index: int | None = None, 
            speed_factor: float | None = None,
            light_pattern: str | None = None, 
            brightness_pattern: str | None = None,
        ):
        """Effects the specified command, mode or pattern(s)."""
        self.sign = create_sign()
        if command is not None:
            self.execute_command(command)
        elif mode_index is not None:
            assert speed_factor is not None
            self.execute_mode(mode_index, speed_factor)
        else:
            self.execute_pattern(light_pattern, brightness_pattern)

    def execute_command(self, command: str):
        """"""
        self.commands[command]()

    def execute_mode(self, mode_index: int, speed_factor: float):
        """"""
        self.player = Player(
            modes=self.modes,
            sign=self.sign, 
            speed_factor=speed_factor,
        )
        self.register_mode_functions()
        self.player.start(mode_index)

    def execute_pattern(self, light_pattern: str | None, brightness_pattern: str | None):
        """"""
        # ??? flip order and remove wait?
        if brightness_pattern is not None:
            print(f"Setting dimmers {brightness_pattern}")
            self.sign.set_dimmers(brightness_pattern)
            self.sign.button_interrupt_wait(TRANSITION_DEFAULT)
        if light_pattern is not None:
            print(f"Setting lights {light_pattern}")
            self.sign.set_lights(light_pattern)

    def register_mode_ids(self):
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
        self.add_mode_ids(17, "build_NEQ")
        self.add_mode_ids(18, "build_EQ")
        self.add_mode_ids(19, "random_fade")
        self.add_mode_ids(20, "random_fade_steady")
        self.add_mode_ids(21, "even_odd_fade")
        self.add_mode_ids(22, "corner_rotate_fade")
        self.add_mode_ids(23, "rotate_slight_fade")

    def register_mode_functions(self):
        """Register the operating modes."""
        player = self.player
        sign = self.player.sign
        self.add_mode_func(0, "selection", player._mode_selection)
        self.add_sequence_mode_func(1, "all_on", seq_all_on)
        self.add_sequence_mode_func(2, "all_off", seq_all_off)
        self.add_sequence_mode_func(3, "even_on", seq_even_on)
        self.add_sequence_mode_func(4, "even_off", seq_even_off)
        self.add_sequence_mode_func(5, "blink_all", 
            seq_blink_all, pace=1,
        )
        self.add_sequence_mode_func(6, "blink_alternate", 
            seq_blink_alternate, pace=1, 
        )
        self.add_sequence_mode_func(7, "rotate",
            lambda: seq_rotate("1100000000"), pace=0.5,
        )
        self.add_sequence_mode_func(8, "random_flip",
            lambda: seq_random_flip(sign.light_pattern), pace=0.5,
        )
        self.add_sequence_mode_func(9, "demo",
            lambda: seq_random_flip(sign.light_pattern), pace=0.5,
        )
        self.add_sequence_mode_func(10, "blink_alternate_fade",
            seq_blink_alternate, pace=4, 
            override=RelayOverride(
                transition_on=1.0,
                transition_off=3.0,
            )
        )
        self.add_sequence_mode_func(11, "random_flip_fade",
            lambda: seq_random_flip(sign.light_pattern), pace=2.0,
            override=RelayOverride(),
        )
        self.add_sequence_mode_func(12, "blink_all_fade_seq",
            seq_blink_all, pace=1,
            override=RelayOverride(
                concurrent=False,
                transition_on=0.5,
                transition_off=0.5,
            )
        )
        self.add_sequence_mode_func(13, "blink_all_fade_con", 
            seq_blink_all, pace=1,
            override=RelayOverride(
                concurrent=True,
                transition_on=0.5,
                transition_off=0.5,
            )
        )
        self.add_sequence_mode_func(14, "blink_all_fade_fast", 
            seq_blink_all, pace=0.5,
            override=RelayOverride()
        )
        self.add_sequence_mode_func(15, "blink_all_fade_slowwww", 
            seq_blink_all, pace=10,
            override=RelayOverride(
                brightness_on=100,
                brightness_off=10,
            )
        )
        self.add_sequence_mode_func(16, "blink_all_fade_stealth", 
            seq_blink_all, pace=(1, 60),
            override=RelayOverride(
                transition_on=2,
                transition_off=2,
            )
        )
        self.add_mode_func(17, "build_NEQ", lambda: build1(player, False))
        self.add_mode_func(18, "build_EQ", lambda: build1(player, True))
        self.add_mode_func(19, "random_fade", lambda: mode_random_fade(player))
        self.add_mode_func(20, "random_fade_steady", lambda: mode_random_fade(player, 2.0))
        self.add_mode_func(21, "even_odd_fade", lambda: mode_even_odd_fade(player))
        self.add_sequence_mode_func(22, "corner_rotate_fade", 
            seq_opposite_corner_pairs, pace=5,
            override=RelayOverride(
                concurrent=True,
                brightness_on = 90,
                brightness_off = 10,
            )
        )
        self.add_sequence_mode_func(23, "rotate_slight_fade",
            seq_rotate, pace=0.5,
            override=RelayOverride(
                concurrent=False,
                brightness_on = 100,
                brightness_off = 30,
            )
        )
