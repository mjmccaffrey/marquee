"""Marquee Lighted Sign Project - marquee (main)"""
"""
marquee
    arguments
    Executor
    Player
        BellSet
        ButtonSet
            Buttons
        DrumSet
        LightController
            HueBridge
            ShellyDimmer
        LightChannel
            HueChannel
            ShellyChannel
        LightSet
            LightController
            LightChannel
            Relays
        BaseMode
            BackgroundMode
            ForegroundMode
                SelectMode
                PerformanceMode
                    DynamicMode
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

from argument import display_help, process_arguments
from devices.button import Shutdown
from executor import Executor, SigTerm
from player import Player
from setup_modes import setup_modes
from setup_devices_hue import setup_devices

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
            try:
                exec.execute(**args)
            except SigTerm:
                print("Exiting.")
            except Shutdown:
                print("Shutting down.")
                os.system("sudo shutdown --halt")
    finally:
        try:
            exec.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()

