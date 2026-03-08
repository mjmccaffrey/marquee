"""Marquee Lighted Sign Project - music_implementation"""

from collections.abc import Callable
from dataclasses import replace
from itertools import chain
import time
from typing import Any, Iterator

from task import Task
from modes.foregroundmode import ForegroundMode
from .music_elements import (
    ActionNote, BaseNote, Element, Measure, NoteGroup,
    Part, Rest, SequenceMeasure,
)
from specialparams import (
    ActionParams, SpecialParams,
)


def _set_mode(the_mode: ForegroundMode) -> None:
    """Set the Mode object used throughout this module."""
    global mode
    mode = the_mode

def prepare_parts(parts: tuple[Part, ...]) -> tuple[Measure, ...]:
    """Expand SequenceMeasures.
       Make all parts the same length.
       Merge parts into single sequence of Measures."""
    for part in parts:
        expand_sequence_measures(part.measures)
        validate_measures(part.measures)
    equalize_part_lengths(parts)
    concurrent_measures = zip(*(part.measures for part in parts))
    return tuple(
        merge_concurrent_measures(measure_set)
        for measure_set in concurrent_measures
    )


def merge_concurrent_measures(measures: tuple[Measure, ...]) -> Measure:
    """Convert measure from each part into single measure
    of (non-rest) notes with 0 duration, padded with rests."""

    def get_concurrent_notes(beat: float) -> list[BaseNote]:
        """Return all notes occuring on beat."""
        result = []
        for i, _ in enumerate(measures):
            if beat_next[i] == beat:
                element = next(elements_in[i], None)
                if element is None:
                    beat_next[i] = None
                else:
                    assert isinstance(element, BaseNote)
                    beat_next[i] = beat + element.duration
                    if not isinstance(element, Rest):
                        result.append(replace(element, duration=0))
        return result

    def convert_concurrent_notes(concurrent: list[BaseNote]) -> Element | None:
        """Return > 1 notes as NoteGroup, 
            1 note as itself, and 0 notes as None."""
        if len(concurrent) > 1:
            result = NoteGroup(tuple(concurrent))
        elif len(concurrent) == 1:
            result = concurrent[0]
        else:
            result = None
        return result

    beats = measures[0].beats
    assert all(m.beats == beats for m in measures)
    elements_in: list[Iterator] = [iter(m.elements) for m in measures]
    elements_out: list[Element] = []
    beat_next: list[float | None] = [0.0 for _ in measures]
    beat, rest_accumulated = 0.0, 0.0
    while any(bn is not None for bn in beat_next):
        concurrent = get_concurrent_notes(beat)
        out = convert_concurrent_notes(concurrent)
        if out is not None:
            if rest_accumulated:
                elements_out.append(Rest(rest_accumulated))
                rest_accumulated = 0.0
            elements_out.append(out)
        next_beat = min(
            (bn for bn in beat_next if bn is not None),
            default=beats
        )
        rest_accumulated += next_beat - beat
        beat = next_beat
    if rest_accumulated:
        elements_out.append(Rest(rest_accumulated))
    return Measure(tuple(elements_out), beats=beats)


def expand_sequence_measures(measures: tuple[Measure, ...]) -> None:
    """Populate SequenceMeasures with ActionNotes."""
    sequence_measures = (
        m for m in measures if isinstance(m, SequenceMeasure)
    )
    for measure in sequence_measures:
        elements = tuple(
            ActionNote(
                duration=measure.step_duration,
                actions=(
                    _light(
                        next(measure.patterns),
                        measure.special,
                    ),
                )
            )
            for _ in range(measure.count)
        )
        object.__setattr__(measure, 'elements', elements)


def validate_measures(measures: tuple[Measure, ...]) -> None:
    """Confirm that measures are ready to play."""
    assert all(
        isinstance(element, BaseNote)
        for measure in measures
        for element in measure.elements
    )
    # assert all(
    #     sum(note.duration) <= measure.beats  # type: ignore
    #     for measure in measures
    #     for note in measure.elements
    # )


def equalize_part_lengths(parts: tuple[Part, ...]) -> None:
    """Make all parts have the same # of measures."""
    longest = max(len(part.measures) for part in parts)
    for part in parts:
        if len(part.measures) < longest:
            pad = Measure(elements=(), beats=part.measures[-1].beats)
            measures = tuple(
                part.measures[i] if i < len(part.measures) else pad
                for i in range(longest)
            )
            object.__setattr__(part, 'measures', measures)


def tasks_in_measure(
    measure: Measure, 
    bps: float, 
    start: float,
) -> list[Task]:
    """Return tasks for all notes in measure."""
    print(bps, start)
    beat = 0.0 
    result = []
    for element in measure.elements:
        assert isinstance(element, (BaseNote, NoteGroup))
        if not isinstance(element, Rest):
            result.append(
                Task(
                    due = start + beat / bps,
                    action = element.play,
                    owner = mode,
                )
            )
        beat += element.duration
        if beat > measure.beats:
            raise ValueError("Too many actual beats in measure.")
    return result


def tasks_in_measures(
    measures: tuple[Measure, ...], 
    bps: float,
    start: float,
) -> list[Task]:
    """Return tasks for all notes in all measures."""
    duration = measures[0].beats / bps
    tasks_by_measure = chain(
        tasks_in_measure(measure, bps, start + i * duration)
        for i, measure in enumerate(measures)
    )
    tasks_combined = [
        task
        for measure in tasks_by_measure
        for task in measure
    ]
    return tasks_combined


def play_measures(measures: tuple[Measure, ...], tempo: int) -> float:
    """Convert measures to tasks, add to task queue.
       Return the # of seconds when playing the last measure
       will be finished, i.e. when a repeat or the next 
       section of music could start."""
    bps = tempo / 60
    start = time.time()
    print(f"{start=}")
    tasks = tasks_in_measures(measures, bps, start)
    for t in tasks:
        print(t.due)
    mode.tasks.bulk_add(tasks)
    return measures[0].beats * len(measures) / bps


def _dimmer(pattern: str) -> Callable:
    """Return callable to effect dimmer pattern."""
    brightness = [
        mode.lights.controller.bulb_model.adjustments[b]
        for b in pattern
    ]
    return lambda: mode.lights.set_channels(brightness=brightness)


def _dimmer_sequence(brightness: int, trans: float) -> Callable:
    """Return callable to effect state of specified channels."""

    def set_channels(lights: list[int]):
        """"""
        mode.lights.set_channels(
            brightness=brightness, 
            transition=trans,
            channel_indexes=set(lights),
        )

    return set_channels


def _dimmer_sequence_flip(trans: float) -> Callable:
    """Return callable to flip state of specified channels."""

    def set_channels(lights: list[int]):
        """"""
        brightness = 0 if mode.lights.brightnesses()[lights[0]] else 100
        mode.lights.set_channels(
            brightness=brightness, 
            transition=trans,
            channel_indexes=set(lights),
        )
    return set_channels


def _light(
    pattern: Any,
    special: SpecialParams | None = None,
) -> Callable:
    """Return callable to effect light pattern."""
    if isinstance(special, ActionParams):
        result = lambda: special.action(pattern)
    else:
        result = lambda: mode.lights.set_relays(
            light_pattern=pattern,
            special=special,
        )
    return result

