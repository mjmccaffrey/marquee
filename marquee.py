"""Marquee Lighted Sign Project - main"""

from arguments import display_help, process_arguments
from executors import Executor, create_sign
from players import Player

def main():
    """Execute Marquee application."""
    try:
        exec = Executor(create_sign, Player)
        try:
            arg = process_arguments(exec.mode_ids, exec.commands)
        except ValueError:
            display_help(exec.mode_menu, exec.commands)
        else:
            exec.execute(**arg)
    finally:
        try:
            exec.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
