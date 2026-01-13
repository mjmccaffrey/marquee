"""Marquee Lighted Sign Project - setup_modes"""

from color import Colors
from executor import Executor
from lightset_misc import LIGHT_COUNT
from modes import (
    ChainMode, ChristmasSongs, EvenOddFade, RotateReversible, 
    RandomFade, Signs, SilentFadeBuild,
    BrightnessSelectMode, ModeSelectMode,
)
from modes.mode_misc import ModeIndex
from sequences import (
    all_on, all_off, blink_all, blink_alternate, even_on, even_off,
    rotate, random_flip, rotate_sides,
)
from specialparams import ChannelParams, EmulateParams, MirrorParams


def setup_modes(exec: Executor) -> None:
    """Register all modes."""
    register_special_modes(exec)
    register_channel_modes(exec)

    # exec.add_mode("christmas", ChristmasSongs)
    # exec.add_mode("pacman", PacManGame)

    register_color_modes(exec)
    register_relay_modes(exec)
    # register_interactive_modes(exec)
    register_silent_modes(exec)
    register_test_modes(exec)
    # register_pyohio_2025_presentation_modes(exec)

def register_special_modes(exec: Executor) -> None:
    """"""
    exec.add_mode("select_mode", ModeSelectMode, 
        index=ModeIndex.SELECT_MODE, hidden=True,
    )
    exec.add_mode("select_brightness", BrightnessSelectMode, 
        index=ModeIndex.SELECT_BRIGHTNESS, hidden=True,
    )
    exec.add_sequence_mode("all_off", all_off,
        index=ModeIndex.DEFAULT,
    )


def register_channel_modes(exec: Executor):
    """"""
    exec.add_mode("chainmodetest", 
        ChainMode,
        mode_sequence = [
            ("blink_alternate_medium", 12),
            ("random_flip_fade_medium", 12),
        ],
    )
    exec.add_sequence_mode("blink_alternate_medium",
        blink_alternate, delay=4, 
        special=ChannelParams(
            trans_on=1.0,
            trans_off=3.0,
        )
    )
    exec.add_sequence_mode("random_flip_fade_medium", 
        random_flip, delay=2.0,
        special=ChannelParams(),
        light_pattern='LIGHT_PATTERN',
    )
    exec.add_sequence_mode("blink_all_fade_fast", 
        blink_all, delay=0.5,
        special=ChannelParams()
    )
    exec.add_sequence_mode("blink_all_fade_slowwww", 
        blink_all, delay=10,
        special=ChannelParams(
            brightness_on=100,
            brightness_off=5,
            concurrent=False,
        )
    )
    exec.add_sequence_mode("blink_all_fade_stealth", 
        blink_all, delay=(1, 60),
        special=ChannelParams(
            trans_on=2,
            trans_off=2,
        )
    )
    exec.add_mode("even_odd_fade", EvenOddFade, delay=0.5)
    # exec.add_mode("random_fade_steady", RandomFade, trans=2)
    exec.add_sequence_mode("rotate_sides_silent", rotate_sides, delay=2.0, pattern='0', clockwise=False,
        special=ChannelParams(
            brightness_on = 90,
            brightness_off = 10,
            trans_on=1.0,
            trans_off=1.0,
        )
    )


def register_color_modes(exec: Executor) -> None:
    """"""
    exec.add_sequence_mode("all_red", 
        all_on,
        special=ChannelParams(
            brightness_on=100,
            color_on=Colors.RED,
            brightness_off=100,
            color_off=Colors.BLUE,
        )
    )
    exec.add_sequence_mode("red_blue_blink_alternate_slow",
        blink_alternate, delay=5, 
        special=ChannelParams(
            brightness_off=100,
            brightness_on=100,
            color_off=Colors.YELLOW,
            color_on=Colors.BLUE,
            trans_on=0.0,
            trans_off=0.0,
        )
    )
    

def register_relay_modes(exec: Executor) -> None:
    """"""
    exec.add_sequence_mode("all_on", all_on)
    exec.add_sequence_mode("even_on", even_on)
    exec.add_sequence_mode("even_off", even_off)
    exec.add_sequence_mode("blink_all", blink_all, delay=1)
    exec.add_sequence_mode("blink_alternate", blink_alternate, delay=1)
    exec.add_sequence_mode(
        "blink_alternate_emulate", 
        blink_alternate, 
        delay=2,
        special=EmulateParams(),
    )
    exec.add_sequence_mode("rotate", rotate, 
        delay=0.5, pattern="110000000000",
    )
    exec.add_sequence_mode("random_flip", random_flip, 
        delay=0.5, light_pattern='LIGHT_PATTERN',
    )
    exec.add_sequence_mode("center_rotate_fade", rotate, 
        delay=0.5, pattern = "010" * 4,
    )
    exec.add_mode("rotate_reversible_1", 
        RotateReversible, delay=0.35, 
        pattern = "1" + "0" * (LIGHT_COUNT - 1))
    exec.add_sequence_mode("rotate_sides", rotate_sides, delay=1.0, pattern='1', clockwise=True)


def register_silent_modes(exec: Executor) -> None:
    """"""
    exec.add_sequence_mode("silent_blink_alternate_slow",
        blink_alternate, delay=10, 
        special=ChannelParams(
            trans_on=2.0,
            trans_off=3.0,
        )
    )
    exec.add_sequence_mode("silent_random_flip_medium", random_flip, delay=2.0,
        special=ChannelParams(
            trans_on=2.0,
            trans_off=2.0,
            concurrent=False,
        ),
        light_pattern='LIGHT_PATTERN',
    )
    exec.add_sequence_mode("silent_random_flip_fast", random_flip, delay=0.25,
        special=ChannelParams(),
        light_pattern='LIGHT_PATTERN',
    )
    exec.add_sequence_mode("silent_blink_all_slowwww", 
        blink_all, delay=4.0,
        special=ChannelParams(
            trans_on=4.0,
            trans_off=4.0,
            brightness_on=100,
            brightness_off=10,
        )
    )
    exec.add_mode("silent_fade_build", 
        SilentFadeBuild,
    )
    exec.add_sequence_mode("silent_rotate_slight_fade",
        rotate, delay=0.5, 
        special=ChannelParams(
            concurrent=False,
            brightness_on = 100,
            brightness_off = 20,
        ),
        pattern='110000000000',
    )
    exec.add_mode("random_bright_fixed_trans", RandomFade, transition=0.5)
    exec.add_mode("random_bright_fixed_dur", RandomFade, duration=5.0)
    exec.add_mode("random_random_random", RandomFade)


def register_test_modes(exec: Executor) -> None:
    """"""
    # exec.add_mode("bell_test", BellTest)


def register_pyohio_2025_presentation_modes(exec: Executor) -> None:
    """PyOhio 2025 presentation."""
    exec.add_sequence_mode("section_1", all_off)
    exec.add_sequence_mode("10_on", lambda: iter(["101111101111"]),
        special=MirrorParams(),
    )
    exec.add_sequence_mode("10_rotate", rotate, 
        pattern="110111110111", delay=1.0, stop=3,
        special=MirrorParams(),
    )
    exec.add_sequence_mode("12_on", all_on,
        special=MirrorParams(),
    )
    exec.add_sequence_mode("rotate_sides", rotate_sides, 
        delay=0.75, pattern='1', clockwise=False,
        special=MirrorParams(),
    )
    exec.add_sequence_mode("section_2", all_off)
    exec.add_mode("12_random_random_trans", RandomFade)
    exec.add_sequence_mode("blink_all_fade_sequential",
        blink_all, delay=1,
        special=ChannelParams(concurrent=False),
    )
    exec.add_sequence_mode("blink_all_fade_consecutive", 
        blink_all, delay=1,
        special=ChannelParams(concurrent=True),
    )
    exec.add_sequence_mode("section_3", all_off)
    exec.add_mode("signs", Signs, special=ChannelParams())
    exec.add_sequence_mode("section_4", all_off)

