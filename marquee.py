"""Marquee Lighted Sign Project - marquee (main)"""

import enum
import logging
import sys

from argument import display_help, process_arguments
from executor import Executor
from modes import define_modes
from player import Player


class ExitCode(enum.IntEnum):
    """Application exit codes."""
    NORMAL = 0
    UNEXPECTED = 1
    INVALID = 2
    SHUTDOWN = 3


def setup_logging() -> logging.Logger:
    """Setup logging."""
    log = logging.getLogger('marquee')
    log.setLevel(logging.DEBUG)
    filelog = logging.FileHandler('marquee.log')
    filelog.setLevel(logging.DEBUG)
    conlog = logging.StreamHandler()
    conlog.setLevel(logging.INFO)
    format = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    filelog.setFormatter(format)
    conlog.setFormatter(format)
    log.addHandler(filelog)
    log.addHandler(conlog)
    return log


def execute(exec: Executor) -> ExitCode:
    """Validate arguments, execute. Return exit code."""
    try:
        kwargs = process_arguments(
            exec.mode_ids,
            exec.color_ids,
            exec.commands,
        )
    except ValueError:
        display_help(
            exec.mode_menu, 
            exec.color_menu, 
            exec.commands,
        )
        return ExitCode.INVALID
    else:
        print()
        print(kwargs)
        print()
        shutdown = exec.execute(**kwargs)
        return ExitCode.SHUTDOWN if shutdown else ExitCode.NORMAL


def cleanup(exec: Executor) -> None:
    """Attempt cleanup through executor."""
    try:
        exec.close()
    except Exception:
        pass


def main() -> ExitCode:
    """Execute Marquee application."""
    result = ExitCode.UNEXPECTED
    try:
        log = setup_logging()
        exec = Executor(Player)
        define_modes(exec)
        result = execute(exec)
    finally:
        cleanup(exec)
        match result:
            case ExitCode.NORMAL:
                log.error("Exiting without shutdown.")
            case ExitCode.UNEXPECTED: 
                log.error("Exiting with unexpected error.")
                raise
            case ExitCode.INVALID:
                log.error("Invalid arguments.")
            case ExitCode.SHUTDOWN:
                log.error("Exiting with shutdown.")
            case _:
                raise RuntimeError
    return result


if __name__ == "__main__":
    sys.exit(main())

