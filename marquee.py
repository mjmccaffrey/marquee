"""Marquee Lighted Sign Project - marquee (main)"""
"""
marquee
    Executor
    Player
        Event
        Task
        ButtonSet
            Button
    devices
        LightController
            HueBridge
            ShellyController
        LightChannel
            HueChannel
            ShellyChannel
        RelayClient
            RelayModule
                NumatoUSBRelayModule
    instruments
        LightSet
        ActionInstrument
        RelayInstrument
            BellSet
            DrumSet
        Releaseable Instrument
            BellSet
        RestInstrument
    modes
        BaseMode
            BackgroundMode
            ForegroundMode
                SelectMode
                PerformanceMode
                    GameMode
                    MusicMode
                    SequenceMode
    music
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
from device_defs import define_devices
from mode_defs import define_modes


def setup_logging() -> None:
    """Setup logging."""
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
    try:
        setup_logging()
        exec = Executor(Player, define_devices)
        define_modes(exec)
        try:
            args = process_arguments(exec.mode_ids, exec.commands)
        except ValueError:
            display_help(exec.mode_menu, exec.commands)
            result = 2
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
        case 2: pass
        case 3: log.error("Exiting with shutdown.")
    return result

if __name__ == "__main__":
    sys.exit(main())

