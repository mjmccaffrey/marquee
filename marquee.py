"""Marquee Lighted Sign Project - main"""
"""
    marquee
        arguments
        Executor
            Player
                Modes
                    mode_defs
                    sequence_defs
            Sign
                Buttons
                Dimmers
                Relays
"""
from arguments import display_help, process_arguments
import executors
import players

def main():
    """Execute Marquee application."""
    try:
        exec = executors.Executor(executors.create_sign, players.Player)
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
