"""Marquee Lighted Sign Project - music"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field, replace
from typing import Any

from definitions import SpecialParams
from music.music_implementation import (
    Element, Measure, Part, Section, Sequence, 
    _dimmer, _dimmer_sequence, _dimmer_sequence_flip,
    _light, _play_measures, _set_player
)
from player_interface import PlayerInterface

def set_player(the_player: PlayerInterface):
    """Set the Player object used throughout this module."""
    _set_player(the_player)

def play(*measures: Measure, tempo: int):
    """Play a series of measures."""
    _play_measures(*measures, tempo=tempo)

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
):
    """Produce Section."""
    return Section(
        parts, 
        beats=beats,
        tempo=tempo,
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
    return _dimmer(pattern)

def dimmer_sequence(brightness: int, transition: float) -> Callable:
    """Return callable to effect state of specified dimmers."""
    return _dimmer_sequence(brightness, transition)

def dimmer_sequence_flip(transition: float) -> Callable:
    """Return callable to flip state of specified dimmers."""
    return _dimmer_sequence_flip(transition)

def light(
    pattern: Any,
    special: SpecialParams | None = None,
) -> Callable:
    """Callable to effect light pattern."""
    return _light(pattern, special)
