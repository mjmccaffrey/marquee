"""Marquee Lighted Sign Project - main"""

from arguments import display_help, process_arguments
from executors import Executor

def main():
    """Execute Marquee application."""
    # print("Executing Marquee")
    try:
        exec = Executor()
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
