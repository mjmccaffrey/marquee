"""Marquee Lighted Sign Project - music_interface"""

from collections.abc import Callable
from typing import Any

from .music_elements import (
    Element, Measure, Part, Section, Sequence, 
)
from .music_implementation import (
    _channel_sequence, _channel_sequence_flip, _light, _set_player,
    expand_sequence_measures, play_measures, prepare_parts, validate_measures
)
from playerinterface import PlayerInterface
from specialparams import SpecialParams


def set_player(the_player: PlayerInterface) -> None:
    """Set the Player object used throughout this module."""
    _set_player(the_player)


def play(*measures: Measure, tempo: int) -> None:
    """Process and then play a series of measures."""
    expand_sequence_measures(measures)
    validate_measures(measures)
    play_measures(measures, tempo=tempo)


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
    # return _channel(pattern)


def dimmer_sequence(brightness: int, trans: float) -> Callable:
    """Return callable to effect state of specified channels."""
    return _channel_sequence(brightness, trans)


def dimmer_sequence_flip(trans: float) -> Callable:
    """Return callable to flip state of specified channels."""
    return _channel_sequence_flip(trans)


def light(
    pattern: Any,
    special: SpecialParams | None = None,
) -> Callable:
    """Return callable to effect light pattern."""
    return _light(pattern, special)

