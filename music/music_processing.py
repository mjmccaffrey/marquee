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
    name: str,
    *parts: Part,
    beats: int = 4,
    tempo: int = 60,
) -> Section:
    """Produce Section."""
    return Section(
        name,
        parts, 
        beats=beats,
        tempo=tempo,
    )


def piece(
    *groups: Section | Part,
) -> Piece:
    """Produce Piece."""
    return Piece(groups)


def play_measures(
    measures: tuple[Measure, ...], 
    delay: float, 
    tempo: int,
    devices: DeviceSet,
    schedule: ScheduleTask,
) -> float:
    """Play measures at tempo, using devices and schedule callable.
       Return the length of the music in seconds."""
    if not measures:
        return 0.0
    bps = tempo / 60
    start = time.time() + delay
    playable = _measures_to_playable(measures, devices, schedule)
    tasks = _measures_to_tasks(playable, bps, start)
    for task in tasks:
        schedule(task)
    return measures[0].beats * len(measures) / bps


def _measures_to_playable(
    measures: tuple[Measure, ...], 
    devices: DeviceSet,
    schedule: ScheduleTask,
) -> tuple[PlayableMeasure, ...]:
    """"""
    return tuple(
        _measure_to_playable(measure, devices, schedule)
        for measure in measures
    )


def _measure_to_playable(
    measure: Measure,
    devices: DeviceSet,
    schedule: ScheduleTask,
) -> PlayableMeasure:
    """"""
    # print(f"{measure=}")
    notes = tuple(
        _note_to_playable(e, devices, schedule)
        for e in measure.elements
    )
    return PlayableMeasure(notes=notes, beats=measure.beats)


def _measures_to_tasks(
    measures: tuple[PlayableMeasure, ...], 
    bps: float,
    start: float,
) -> list[MusicTask]:
    """Return tasks for all notes in all measures.
       Begin playing at start; play at speed bps."""
    # if not measures:
    #     return []
    duration = measures[0].beats / bps
    tasks_by_measure = (
        _measure_to_tasks(measure, bps, start + i * duration)
        for i, measure in enumerate(measures)
    )
    return [
        task
        for measure in tasks_by_measure
        for task in measure
    ]

def _measure_to_tasks(
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
    # print(len(result))
    # for i, r in enumerate(result):
    #     print(i, r)
    #     print()
    return result


def _note_to_playable(
    element: Element, 
    devices: DeviceSet,
    schedule: ScheduleTask,
) -> PlayableNote:
    """Return dict of attribute assignments."""
    if type(element) == NoteGroup:
        return _note_group_to_playable(element, devices, schedule)
    else:
        return _single_note_to_playable(element, devices, schedule)


def _single_note_to_playable(
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


def _note_group_to_playable(
        element, devices, schedule,
) -> PlayableNoteGroup:
    """"""
    note = cast(NoteGroup, element)
    playable_notes = tuple(
        _note_to_playable(n, devices, schedule)
        for n in note.notes
    )
    args = asdict(note) | dict(notes=playable_notes)
    return PlayableNoteGroup(**args)  # type: ignore


