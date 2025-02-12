"""Marquee Lighted Sign Project - main"""

import contextlib
import os
import sys
import time

from arguments import display_help, process_runtime_arguments
from modes import register_modes
from players import Player

def main():
    """Execute Marquee application."""
    try:
        print(time.time())
        player = Player()
        print(time.time())
        register_modes(player)
        if arg := process_runtime_arguments(player):
            player.execute(**arg)
        else:
            display_help(player)
    finally:
        player.close()  # !!! ignore errors

if __name__ == "__main__":
    main()
