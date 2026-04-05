"""Marquee Lighted Sign Project - marquee (main)"""

import logging
import sys

from argument import display_help, process_arguments
from executor import Executor
from player import Player
from device_defs import define_devices
from mode_defs import define_modes


def setup() -> Executor:
    """Setup logging, executor, modes. Return executor."""
    setup_logging()
    exec = Executor(Player, define_devices)
    define_modes(exec)
    return exec


def setup_logging() -> None:
    """Setup logging."""
    global log
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


def execute(exec: Executor) -> int:
    """Validate arguments, execute. Return exit code."""
    try:
        args = process_arguments(exec.mode_ids, exec.commands)
    except ValueError:
        display_help(exec.mode_menu, exec.commands)
        return 2
    else:
        shutdown = exec.execute(**args)
        return 3 if shutdown else 0


def cleanup(exec: Executor) -> None:
    """Attempt cleanup through executor."""
    try:
        exec.close()
    except Exception:
        pass


def main() -> int:
    """Execute Marquee application."""
    result = 1
    try:
        exec = setup()
        result = execute(exec)
    finally:
        cleanup(exec)
        match result:
            case 0: log.error("Exiting without shutdown.")
            case 1: 
                log.error("Exiting with unexpected error.")
                raise
            case 2: log.error("Invalid arguments.")
            case 3: log.error("Exiting with shutdown.")
        return result


if __name__ == "__main__":
    sys.exit(main())

