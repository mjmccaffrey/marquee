"""Marquee Lighted Sign Project - main"""

import sys
import time
import types

from modes import *
import players
from sequences import *

def display_help():
    """"Display the command-line syntax."""
    print()
    print("Usage: marquee.py {mode_index | mode_name | light_pattern}\n")
    print("Valid modes:")
    for index, entry in self.mode_table.items():
        if index != 0:
            print(f'{index}\t{entry.name}')
    print()

def register_modes(player):
    """Register the operating modes."""
    player.add_mode(1, "all_on", simple_mode(seq_all_on))
    player.add_mode(2, "even_on", simple_mode(seq_even_on))
    player.add_mode(3, "even_off", simple_mode(seq_even_off))
    player.add_mode(4, "all_off", simple_mode(seq_all_off))
    player.add_mode(6, "blink_all", simple_mode(seq_blink_all, pace=1))
    player.add_mode(6, "blink_alternate", simple_mode(seq_blink_alternate, pace=1))
    player.add_mode(7, "demo", lambda: mode_rhythmic_demo(sign))

def process_runtime_argument():
    """Validate the runtime argument.
       If a light pattern is specified, set the lights accordingly.
       Return False if the application should terminate, otherwise True."""
    if len(sys.argv) != 2:
        return False
    arg = sys.argv[1]
    if self.sign.is_valid_light_pattern(arg):
        player_args = {"pattern": arg}
    elif arg in mode.id_to_index:
        player_args = {"mode": mode.id_to_index[arg]}
    else:
        return False
    return player_args

def main():
    """Execute Marquee application."""
    # # HACK - give Pi Zero time for relay board to show up during boot
    # time.sleep(1)
    #
    try:
        player = players.Player()
        register_modes()
        arg = process_runtime_argument()
        if arg:
            player.execute(**arg)
        else:
            display_help()
    finally:
        player.close()

if __name__ == "__main__":
    main()
