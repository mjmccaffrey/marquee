"""Marquee Lighted Sign Project - music_processing"""

from dataclasses import asdict
from functools import partial
import logging
import time
from typing import cast

from devices.device_schemas import DeviceSet
from modes import Mode
from .music_abstract import Scheduled
from .music_concrete import (
    Note, Element, NOTE_CONVERSIONS,
    Part, Section, Piece, Measure, 
    PlayableMeasure, PlayableNote, PlayableRest, 
)
from task import Task, TaskSchedule


log = logging.getLogger('marquee.' + __name__)


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


def play(
        measures: tuple[Measure, ...], 
        delay: float, 
        tempo: int,
        devices: DeviceSet,
        schedule: TaskSchedule,
        owner: Mode,
) -> float:
    """Convert measures to tasks, add to task queue.
       Return the # of seconds from start when playing the last measure
       will be finished, i.e. when a repeat or the next 
       section of music could start."""
    bps = tempo / 60
    start = time.time() + delay
    playable = convert_measures_to_playable(
        measures, devices, schedule,
    )
    tasks = convert_measures_to_tasks(playable, bps, start, owner)
    schedule.bulk_add(tasks)
    return measures[0].beats * len(measures) / bps


def _convert_note_to_playable(
    element: Element, 
    devices: DeviceSet,
    schedule: TaskSchedule,
) -> PlayableNote:
    """Return dict of attribute assignments."""
    note = cast(Note, element)
    try:
        args = (
            asdict(note) | 
            dict(instrument=devices[note.device]) |
            (
                dict(schedule=schedule) 
                if isinstance(note, Scheduled) else 
                {}
            )
        )
    except ValueError:
        raise ValueError(f"No {note.device} instrument present.")
    return NOTE_CONVERSIONS[type(element)](**args)  # type: ignore


def _convert_measure_to_playable(
    measure: Measure,
    devices: DeviceSet,
    schedule: TaskSchedule,
) -> PlayableMeasure:
    """"""
    notes = tuple(
        _convert_note_to_playable(e, devices, schedule)
        for e in measure.elements
    )
    return PlayableMeasure(notes=notes, beats=measure.beats)


def convert_measures_to_playable(
    measures: tuple[Measure, ...], 
    devices: DeviceSet,
    schedule: TaskSchedule,
) -> tuple[PlayableMeasure, ...]:

    """"""
    return tuple(
        _convert_measure_to_playable(measure, devices, schedule)
        for measure in measures
    )


def _tasks_in_measure(
    measure: PlayableMeasure, 
    bps: float, 
    start: float,
    owner: object,
) -> list[Task]:
    """Return tasks for all (non-rest) notes in measure."""
    beat = 0.0 
    result = []
    for note in measure.notes:
        if not isinstance(note, PlayableRest):
            result.append(
                Task(
                    due = start + beat / bps,
                    action = partial(note.play, bps),
                    owner = owner,
                )
            )
        beat += note.duration
        if beat > measure.beats:
            raise ValueError("Too many actual beats in measure.")
    return result


def convert_measures_to_tasks(
    measures: tuple[PlayableMeasure, ...], 
    bps: float,
    start: float,
    owner: object,
) -> list[Task]:
    """Return tasks for all notes in all measures.
       Begin playing at start; play at speed bps."""
    duration = measures[0].beats / bps
    tasks_by_measure = (
        _tasks_in_measure(measure, bps, start + i * duration, owner)
        for i, measure in enumerate(measures)
    )
    return [
        task
        for measure in tasks_by_measure
        for task in measure
    ]

