"""Marquee Lighted Sign Project - music_processing"""

from dataclasses import replace
from functools import partial
import logging
import time
from typing import Any, cast, Iterator

from devices.devices_misc import DeviceSet
from modes import Mode
from .music_elements import Note, Element, ScheduledNote, Rest
from .music_collections import Measure, NoteGroup, Part, Section, Piece
from task import Task, TaskSchedule


log = logging.getLogger('marquee.' + __name__)


def play_measures(
        measures: tuple[Measure, ...], 
        delay: float, 
        tempo: int,
        schedule: TaskSchedule,
        owner: Mode,
) -> float:
    """Convert measures to tasks, add to task queue.
       Return the # of seconds from start when playing the last measure
       will be finished, i.e. when a repeat or the next 
       section of music could start."""
    bps = tempo / 60
    start = time.time() + delay
    tasks = tasks_in_measures(measures, bps, start, owner)
    schedule.bulk_add(tasks)
    result = measures[0].beats * len(measures) / bps
    return result

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
    )


def piece(
    *groups: Section | Part,
) -> Piece:
    """Produce Piece."""
    return Piece(groups)


def equalize_part_lengths(parts: tuple[Part, ...]) -> None:
    """Make all parts have the same # of measures."""
    longest = max(len(part.measures) for part in parts)
    for part in parts:
        if len(part.measures) < longest:
            pad = Measure(elements=(Rest(0.0),), beats=part.measures[-1].beats)
            measures = tuple(
                part.measures[i] if i < len(part.measures) else pad
                for i in range(longest)
            )
            object.__setattr__(part, 'measures', measures)


def merge_concurrent_measures(measures: tuple[Measure, ...]) -> Measure:
    """Convert measure from each part into single measure
    of (non-rest) notes with 0 duration, padded with rests."""

    def get_concurrent_notes(beat: float) -> list[Note]:
        """Return all notes occuring on beat."""
        result = []
        for i, _ in enumerate(measures):
            if beat_next[i] == beat:
                element = next(elements_in[i], None)
                if element is None:
                    beat_next[i] = None
                else:
                    assert isinstance(element, Note)
                    beat_next[i] = beat + element.duration
                    if not isinstance(element, Rest):
                        result.append(replace(element, duration=0))
        return result

    def convert_concurrent_notes(concurrent: list[Note]) -> Element | None:
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


def resource_assignments(
    element: Element, 
    devices: DeviceSet,
    schedule: TaskSchedule,
) -> dict[str, Any]:
    """Return dict of attribute assignments."""
    note = cast(Note, element)
    result = dict(instrument=devices[note.device])
    if isinstance(note, ScheduledNote):
        result |= dict(schedule=schedule)
    return result


def assign_resources(
    measures: tuple[Measure, ...], 
    devices: DeviceSet,
    schedule: TaskSchedule,
) -> None:
    """"""
    for measure in measures:
        elements = tuple(
            replace(e, **resource_assignments(e, devices, schedule))
            for e in measure.elements
        )
        object.__setattr__(measure, 'elements', elements)


def prepare_parts(
    parts: tuple[Part, ...], 
    devices: DeviceSet,
    schedule: TaskSchedule,
) -> tuple[Measure, ...]:
    """Process parts: prepare measures; make each part the same
       number of measures; merge parts into single sequence of Measures."""
    for part in parts:
        prepare_measures(part.measures, devices, schedule)
    equalize_part_lengths(parts)
    concurrent_measures = zip(*(part.measures for part in parts))
    return tuple(
        merge_concurrent_measures(measure_set)
        for measure_set in concurrent_measures
    )


def prepare_measures(
    measures: tuple[Measure, ...],
    devices: DeviceSet,
    schedule: TaskSchedule,
) -> tuple[Measure, ...]:
    """Assign an instrument to each note.
       Confirm that measures are ready to play."""
    assign_resources(measures, devices, schedule)
    # assert all(
    #     sum(note.duration) <= measure.beats  # type: ignore
    #     for measure in measures
    #     for note in measure.elements
    # )
    return measures


def tasks_in_measure(
    measure: Measure, 
    bps: float, 
    start: float,
    owner: object,
) -> list[Task]:
    """Return tasks for all notes in measure."""
    beat = 0.0 
    result = []
    for element in measure.elements:
        assert isinstance(element, (Note, NoteGroup))
        if not isinstance(element, Rest):
            result.append(
                Task(
                    due = start + beat / bps,
                    action = partial(element.play, bps),
                    owner = owner,
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
    owner: object,
) -> list[Task]:
    """Return tasks for all notes in all measures."""
    duration = measures[0].beats / bps
    tasks_by_measure = (
        tasks_in_measure(measure, bps, start + i * duration, owner)
        for i, measure in enumerate(measures)
    )
    tasks_combined = [
        task
        for measure in tasks_by_measure
        for task in measure
    ]
    return tasks_combined

