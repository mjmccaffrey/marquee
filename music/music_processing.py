"""Marquee Lighted Sign Project - music_processing"""

from dataclasses import asdict
from functools import partial
import logging
import time
from typing import cast

from devices.deviceset import DeviceSet
from modes import Mode
from .music_abstract import MusicTask, Scheduled, ScheduleTask
from .music_concrete import (
    Note, NoteGroup, Element, NOTE_CONVERSIONS,
    Part, Section, Piece, Measure, 
    PlayableMeasure, PlayableNote, PlayableNoteGroup, PlayableRest,
)
from schemas import EpochTime


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
        schedule: ScheduleTask,
) -> float:
    """Convert measures to tasks, add to task queue.
       Return the # of seconds from start when playing the last measure
       will be finished, i.e. when a repeat or the next 
       section of music could start."""
    if not measures:
        return 0.0
    bps = tempo / 60
    start = time.time() + delay
    playable = convert_measures_to_playable(
        measures, devices, schedule,
    )
    tasks = convert_measures_to_tasks(playable, bps, start)
    print(len(tasks))
    print(time.time())
    for task in tasks:
        schedule(task)
    print(time.time())
    return measures[0].beats * len(measures) / bps


def _convert_note_to_playable(
    element: Element, 
    devices: DeviceSet,
    schedule: ScheduleTask,
) -> PlayableNote:
    """Return dict of attribute assignments."""
    if type(element) == NoteGroup:
        return _convert_note_group_to_playable(element, devices, schedule)
    else:
        return _convert_single_note_to_playable(element, devices, schedule)


def _convert_single_note_to_playable(
    element, devices, schedule,
) -> PlayableNote:
    """"""
    playable_type = NOTE_CONVERSIONS[type(element)]
    note = cast(Note, element)
    if note.device is None:
        instrument = None 
    else:
        try:
            instrument = devices[note.device.value]
        except KeyError:
            raise ValueError(f"No {note.device} instrument present.")
    playable_args = dict(instrument=instrument)
    if issubclass(playable_type, Scheduled):
        playable_args |= dict(schedule=schedule) 
    args = asdict(note) | playable_args
    return playable_type(**args)  # type: ignore


def _convert_note_group_to_playable(
        element, devices, schedule,
) -> PlayableNoteGroup:
    """"""
    note = cast(NoteGroup, element)
    playable_notes = tuple(
        _convert_note_to_playable(n, devices, schedule)
        for n in note.notes
    )
    args = asdict(note) | dict(notes=playable_notes)
    return PlayableNoteGroup(**args)  # type: ignore


def _convert_measure_to_playable(
    measure: Measure,
    devices: DeviceSet,
    schedule: ScheduleTask,
) -> PlayableMeasure:
    """"""
    print(f"{measure=}")
    notes = tuple(
        _convert_note_to_playable(e, devices, schedule)
        for e in measure.elements
    )
    return PlayableMeasure(notes=notes, beats=measure.beats)


def convert_measures_to_playable(
    measures: tuple[Measure, ...], 
    devices: DeviceSet,
    schedule: ScheduleTask,
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
) -> list[MusicTask]:
    """Return tasks for all (non-rest) notes in measure."""
    beat = 0.0 
    result = []
    for note in measure.notes:
        if not isinstance(note, PlayableRest):
            result.append(
                MusicTask(
                    action=partial(note.play, bps),
                    due=EpochTime(start + beat / bps),
                )
            )
        beat += note.duration
        if beat > measure.beats:
            raise ValueError("Too many actual beats in measure.")
    print(len(result))
    for i, r in enumerate(result):
        print(i, r)
        print()
    return result


def convert_measures_to_tasks(
    measures: tuple[PlayableMeasure, ...], 
    bps: float,
    start: float,
) -> list[MusicTask]:
    """Return tasks for all notes in all measures.
       Begin playing at start; play at speed bps."""
    if not measures:
        return []
    duration = measures[0].beats / bps
    tasks_by_measure = (
        _tasks_in_measure(measure, bps, start + i * duration)
        for i, measure in enumerate(measures)
    )
    return [
        task
        for measure in tasks_by_measure
        for task in measure
    ]

