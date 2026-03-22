"""Marquee Lighted Sign Project - marquee (main)"""
"""
marquee
    arguments
    Executor
    Player
        BellSet
        ButtonSet
            Button
        DrumSet
        LightSet
            LightController
            LightChannel
            RelayClient
        LightController
            HueBridge
            ShellyController
        LightChannel
            HueChannel
            ShellyChannel
        RelayClient
            RelayModule
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
import os
import logging

from argument import display_help, process_arguments
from executor import Executor
from player import Player
from setup_devices import setup_devices
from setup_modes import setup_modes

log = logging.getLogger(__name__)


def main() -> None:
    """Execute Marquee application."""
    try:
        exec = Executor(Player, setup_devices)
        setup_modes(exec)
        try:
            args = process_arguments(exec.mode_ids, exec.commands)
        except ValueError:
            display_help(exec.mode_menu, exec.commands)
        else:
            shutdown = exec.execute(**args)
            if shutdown:
                print("Shutting down.")
                os.system("sudo shutdown --halt")
            else:
                print("Exiting without shutdown.")
    finally:
        try:
            exec.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()

