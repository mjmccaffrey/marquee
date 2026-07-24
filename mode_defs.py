"""Marquee Lighted Sign Project - define_modes"""

from devices.color import Colors
from devices.specialparams import ChannelParams, EmulateParams, MirrorParams
from executor import Executor
from modes import *
from modes.pacman import base_maze, passage_maze


def define_modes(exec: Executor) -> None:
    """Register all modes."""
    register_special_modes(exec)
    register_channel_modes(exec)
    register_pyohio_2026_presentation_modes(exec)
    register_pyohio_2026_sign_modes(exec)
    
    exec.add_mode("pacman_12", PacManGame, maze=base_maze)
    exec.add_mode("pacman_15", PacManGame, maze=passage_maze)
    exec.add_mode("doom_12", DoomGame, passage=False)
    exec.add_mode("doom_15", DoomGame, passage=True)

    register_relay_modes(exec)
    register_silent_modes(exec)

def register_special_modes(exec: Executor) -> None:
    """"""
    exec.add_mode("select_mode", ModeSelect, 
        index=ModeIndex.MODE_SELECT, hidden=True,
        previous="PREVIOUS_MODE",
    )
    exec.add_mode("select_brightness", BrightnessSelect, 
        index=ModeIndex.BRIGHTNESS_SELECT, hidden=True,
    )
    exec.add_sequence_mode("all_off", all_off,
        index=ModeIndex.DEFAULT,
    )

def register_pyohio_2026_presentation_modes(exec: Executor) -> None:
    """PyOhio 2026 presentation."""
    exec.add_mode("alarm_dive", AlarmDive)
    exec.add_mode("comet_wheel", Comet,
        length=9,
        delay=0.175,
        wheel_divisions=3,
        direction=-1,
    )
    exec.add_mode("cupola_wheel", CupolaSequence,
        color_set_name='wheel',
        brightness=100,
        transition=1,
        delay=3,
        direction=-1,
    )
    exec.add_mode("cupola_wheel_divisions", CupolaSequence,
        color_set_name='',
        brightness=100,
        transition=1,
        delay=1,
        wheel_divisions=8,
    )
    exec.add_mode("rhythm", Rhythm)
    exec.add_mode("signs", Signs)
    exec.add_mode("twelve", Twelve, brightness=40)
    exec.add_mode("2026_presentation", ModeCycle,
        sequence = [
            ("cupola_wheel_divisions", 0.1),
            ("alarm_dive", 0.1),
            ("rotate_sides_emulate", 60),
            ("silent_random_flip_medium", 60),
            ("twelve", 60),
            ("signs", 60),
            ("random_random_random", 99999),
        ],
    )

def register_pyohio_2026_sign_modes(exec: Executor) -> None:
    """PyOhio 2026 presentation."""
    exec.add_mode("comet_violet", Comet,
        length=4,
        delay=0.1875,
        color=Colors.VIOLET,
        cupola_delay=10.0,
    )
    exec.add_mode("2026_sign", ModeCycle,
        sequence = [
            ("comet_violet", 180),
            ("random_random_random", 180),
            ("silent_fade_build", 180),
        ],
    )

def register_channel_modes(exec: Executor):
    """"""
    cs_sequence = [
        # ("party", 1),
        # ("cancun", 1),
        ("race", 10),
        # ("amber_bloom", 1),
        # ("ALL", 10),
    ]
    exec.add_mode("cs_chase_neg", ColorSetDynamic, 
        sequence=[
        # ("party", 1),
        # ("cancun", 1),
            ("race", 10),
        ],
        pattern='0123456789ab',
        mask='-***********',
        clockwise=True,
        delay=0.4,
        brightness=35,
    )
    exec.add_mode("cs_chase_3", ColorSetDynamic, 
        sequence=[
            ("party", 1),
        # ("cancun", 1),
            # ("race", 10),
        ],
        pattern='012---------',
        clockwise=True,
        delay=0.4,
        brightness=35,
    )
    exec.add_mode("cs_chase_12", ColorSetDynamic, 
        sequence=[
        # ("party", 1),
            ("cancun", 1),
            # ("race", 10),
        ],
        pattern='0123456789ab',
        clockwise=False,
        delay=0.66,
        brightness=35,
    )
    exec.add_mode("cs_all", ColorSetStatic,
        sequence=[
        # ("party", 1),
        # ("cancun", 1),
            ("ALL", 10),
        ],
        brightness=35,
        # transition=0.0,
    )
    exec.add_mode('rotate_sides_emulate', RotateSides, delay=0.8)
    exec.add_sequence_mode("blink_alternate_medium",
        blink_alternate, delay=10, 
        special=ChannelParams(
            # brightness_on=90,
            trans_on=1.0,
            trans_off=3.0,
        )
    )
    exec.add_sequence_mode("random_flip_fade_medium", 
        random_flip, 
        sequence_kwargs=dict(light_pattern='LIGHT_PATTERN'),
        delay=1.0,
        # special=ChannelParams(),
        baseline=None,
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
    exec.add_sequence_mode("rotate_sides_silent", rotate_sides, 
        sequence_kwargs=dict(
            pattern='0', 
            clockwise=False,
        ),
        delay=2.0, 
        special=ChannelParams(
            brightness_on = 90,
            brightness_off = 10,
            trans_on=1.0,
            trans_off=1.0,
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
    exec.add_sequence_mode("random_flip", random_flip, 
        sequence_kwargs=dict(light_pattern='LIGHT_PATTERN'),
        delay=0.5, 
        baseline=None,
    )
    exec.add_sequence_mode("rotate_sides", rotate_sides, 
        sequence_kwargs=dict(
            pattern='1', 
            clockwise=True,
        ),
        delay=1.0, 
    )


def register_silent_modes(exec: Executor) -> None:
    """"""
    exec.add_sequence_mode("silent_blink_alternate_slow",
        blink_alternate, delay=10, 
        special=ChannelParams(
            trans_on=2.0,
            trans_off=3.0,
        )
    )
    exec.add_sequence_mode("silent_random_flip_medium", random_flip, 
        sequence_kwargs=dict(light_pattern='LIGHT_PATTERN'),
        delay=2.0,
        special=ChannelParams(
            trans_on=2.0,
            trans_off=2.0,
            concurrent=False,
        ),
        baseline=None,
    )
    exec.add_sequence_mode("silent_random_flip_fast", random_flip, 
        sequence_kwargs=dict(light_pattern='LIGHT_PATTERN'),
        delay=0.25,
        special=ChannelParams(),
        baseline=None,
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
    exec.add_mode("random_bright_fixed_trans", RandomFade, transition=0.5)
    exec.add_mode("random_bright_fixed_dur", RandomFade, duration=5.0)
    exec.add_mode("random_random_random", RandomFade)
    exec.add_mode("generate", GeneratedModes)
    exec.add_mode("narcissa_random_random", RandomFade, color_set_name='narcissa')

