"""Marquee Lighted Sign Project - main"""

import sys

from modes import *
import players
from sequences import *

def display_help(player):
    """"Display the command-line syntax."""
    print()
    print("Usage: marquee.py {mode_index | mode_name | light_pattern}\n")
    print("Valid modes:")
    for index, entry in player.mode_table.items():
        if index != 0:
            print(f'{index}\t{entry.name}')
    print()

def register_modes(player):
    """Register the operating modes."""
    player.add_mode(1, "all_on", seq_all_on, simple=True)
    player.add_mode(2, "even_on", seq_even_on, simple=True)
    player.add_mode(3, "even_off", seq_even_off, simple=True)
    player.add_mode(4, "all_off", seq_all_off, simple=True)
    player.add_mode(6, "blink_all", seq_blink_all, simple=True, pace=1)
    player.add_mode(6, "blink_alternate", seq_blink_alternate, simple=True, pace=1)
    player.add_mode(7, "demo", lambda: mode_rhythmic_demo(player))

def process_runtime_argument(player):
    """Validate the runtime argument.
       If a light pattern is specified, set the lights accordingly.
       Return False if the application should terminate, otherwise True."""
    if len(sys.argv) != 2:
        return False
    arg = sys.argv[1]
    if player.sign.is_valid_light_pattern(arg):  # !!
        player_args = {"pattern": arg}
    elif arg in player.mode_id_to_index:  # !!
        player_args = {"mode": player.mode_id_to_index[arg]}  # !!
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
        register_modes(player)
        arg = process_runtime_argument(player)
        if arg:
            player.execute(**arg)
        else:
            display_help(player)
    finally:
        player.close()

if __name__ == "__main__":
    main()
