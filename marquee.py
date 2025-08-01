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
            LightSet
                Dimmers
                Relays
            AutoMode
            SelectMode
            PlayMode
            PlaySequenceMode
            PlayMusicMode
                Instrument
                    ActionInstrument
                    RelayInstrument
                        BellSet
                        DrumSet
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
            sequences
"""
from arguments import display_help, process_arguments
from definitions import Shutdown
from executors import Executor, setup_devices
import os
from players import Player
from register_modes import register_modes

def main():
    """Execute Marquee application."""
    try:
        exec = Executor(Player, setup_devices)
        register_modes(exec)
        try:
            args = process_arguments(exec.mode_ids, exec.commands)
        except ValueError:
            display_help(exec.mode_menu, exec.commands)
        else:
            try:
                exec.execute(**args)
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
