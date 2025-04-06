"""Marquee Lighted Sign Project - main"""
"""
marquee
    arguments
    Executor
        Player
            SelectMode
            PlayMode
            PlaySequenceMode
            PlayMusicMode
                Part
                    notation
                    Measure
                        sequence
                            Bell
                            Note
                            Rest
            mode_defs
            sequence_defs
        Sign
            Buttons
            Dimmers
            Relays
"""
from arguments import display_help, process_arguments
from executors import Executor, create_sign
from players import Player

def main():
    """Execute Marquee application."""
    try:
        exec = Executor(create_sign, Player)
        try:
            args = process_arguments(exec.mode_ids, exec.commands)
        except ValueError:
            display_help(exec.mode_menu, exec.commands)
        else:
            exec.execute(**args)
    finally:
        try:
            exec.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
