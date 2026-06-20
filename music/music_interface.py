"""Marquee Lighted Sign Project - music_interface"""

from collections.abc import Callable
import logging
from typing import Any

from modes.abstract.foregroundmode import ForegroundMode
from . import music_elements
from .music_elements import (
    Element, Measure, Part, Section, Piece, Sequence, 
)
from . import music_implementation
from .music_implementation import (
    expand_sequence_measures, play_measures, prepare_parts, 
    _relay, validate_measures
)
from devices.specialparams import SpecialParams

log = logging.getLogger('marquee.' + __name__)


def set_mode(the_mode: ForegroundMode) -> None:
    """Set the Mode object used throughout the music modules."""
    global mode
    mode = the_mode
    music_elements.mode = the_mode
    music_implementation.mode = the_mode


def play(*measures: Measure, tempo: int) -> float:
    """Process and then play a series of measures."""
    expand_sequence_measures(measures)
    validate_measures(measures)
    return play_measures(
        measures, 
        delay=0.0,
        tempo=tempo,
    )


def measure(*elements: Element, beats: int = 4) -> Measure:
    """Produce Measure."""
    return Measure(elements, beats=beats)


def part(*measures: Measure, accent: int = 0) -> Part:
    """Produce Part."""
    return Part(measures, accent)


def section(
    *parts: Part,
    beats: int = 4,
    tempo: int = 60,
) -> Section:
    """Produce Section."""
    return Section(
        parts, 
        beats=beats,
        tempo=tempo,
        prepare_parts=prepare_parts,
        play_measures=play_measures,
    )


def piece(
    *groups: Section | Part,
) -> Piece:
    """Produce Piece."""
    return Piece(
        groups,
        play_measures=play_measures,
    )


def sequence(
    seq: Callable,
    measures: int = 1,
    special: SpecialParams | None = None,
    **kwargs,
) -> Sequence:
    """Return callable to effect each step in sequence."""
    sequence_obj = Sequence(seq, special, measures, kwargs)
    return sequence_obj


def dimmer(pattern: str) -> Callable:
    """Return callable to effect dimmer pattern."""
    brightness = [
        mode.lights.bulb_adjustments[b]
        for b in pattern
    ]
    return lambda: mode.lights.set_channels(brightness=brightness)


def dimmer_sequence(brightness: int, transition: float) -> Callable:
    """Return callable to effect state of specified channels."""

    def set_channels(lights: list[int]):
        """"""
        mode.lights.set_channels(
            brightness=brightness, 
            transition=transition,
            index=lights,
        )

    return set_channels


def dimmer_sequence_flip(transition: float) -> Callable:
    """Return callable to flip state of specified channels."""

    def set_channels(lights: list[int]):
        """"""
        brightness = 0 if mode.lights.brightnesses()[lights[0]] else 100
        mode.lights.set_channels(
            brightness=brightness, 
            transition=transition,
            index=lights,
        )

    return set_channels


def relay(
    pattern: Any,
    special: SpecialParams | None = None,
) -> Callable:
    """Return callable to effect light pattern."""
    return _relay(pattern, special)

