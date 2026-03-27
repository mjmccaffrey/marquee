"""Marquee Lighted Sign Project - marquee (main)"""
"""
marquee
    Executor
    Player
        BellSet
        ButtonSet
            Button
        DrumSet
        LightSet
            LightController
                HueBridge
                ShellyController
            LightChannel
                HueChannel
                ShellyChannel
            RelayClient
                RelayModule
                    NumatoUSBRelayModule
        BaseMode
            BackgroundMode
            ForegroundMode
                SelectMode
                PerformanceMode
                    GameMode
                    MusicMode
                    SequenceMode
        Instrument
            ActionInstrument
            RelayInstrument
                BellSet
                DrumSet
            Releaseable Instrument
                BellSet
            RestInstrument
        Section
            Part
                Measure
                    Element
                        BaseNote
                            ActionNote
                            BellNote
                            DrumNote
                            Rest
                        NoteGroup
                SequenceMeasure
                Sequence
"""
import logging
import sys

from argument import display_help, process_arguments
from executor import Executor
from player import Player
from setup_devices import setup_devices
from setup_modes import setup_modes


def setup_logging() -> None:
    """"""
    global log
    log = logging.getLogger('marquee')
    log.setLevel(logging.DEBUG)
    filelog = logging.FileHandler('marquee.log')
    filelog.setLevel(logging.DEBUG)
    conlog = logging.StreamHandler()
    conlog.setLevel(logging.INFO)
    format = logging.Formatter('%(asctime)s - %(message)s')
    filelog.setFormatter(format)
    conlog.setFormatter(format)
    log.addHandler(filelog)
    log.addHandler(conlog)


def main() -> int:
    """Execute Marquee application."""
    result = 1
    try:
        setup_logging()
        exec = Executor(Player, setup_devices)
        setup_modes(exec)
        try:
            args = process_arguments(exec.mode_ids, exec.commands)
        except ValueError:
            display_help(exec.mode_menu, exec.commands)
        else:
            shutdown = exec.execute(**args)
            result = 3 if shutdown else 0
    finally:
        try:
            exec.close()
        except Exception:
            pass
    match result:
        case 0: log.error("Exiting without shutdown.")
        case 1: log.error("Unexpected error occurred.")
        case 3: log.error("Exiting with shutdown.")
    return result

if __name__ == "__main__":
    sys.exit(main())

