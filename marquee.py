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
    for index, entry in player.modes.items():
        if index != 0:
            print(f'{index}\t{entry.name}')
    print()

def register_modes(player):
    """Register the operating modes."""
    player.add_mode(1, "all_on", seq_all_on, simple=True)
    player.add_mode(2, "even_on", seq_even_on, simple=True)
    player.add_mode(3, "even_off", seq_even_off, simple=True)
    player.add_mode(4, "all_off", seq_all_off, simple=True)
    player.add_mode(5, "blink_all", seq_blink_all, simple=True, pace=1)
    player.add_mode(6, "blink_alternate",
        seq_blink_alternate, simple=True, pace=1
    )
    player.add_mode(7, "rotate",
        lambda: seq_rotate("1000000000"), simple=True, pace=0.75,  # !!!
        use_dimmers=True,
    )
    player.add_mode(8, "random_flip",
        lambda: seq_random_flip(player.current_pattern),
        simple=True, pace=0.5
    )
    player.add_mode(9, "demo", lambda: mode_rhythmic_demo(player))

def process_runtime_argument(player):
    """Validate the runtime argument.
       If a light pattern is specified, set the lights accordingly.
       Return False if the application should terminate, otherwise True."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        return False
    arg1 = sys.argv[1]
    if player.is_valid_light_pattern(arg1):
        player_args = {"light_pattern": arg1}
        if len(sys.argv) == 3:
            arg2 = sys.argv[2]
            if player.is_valid_brightness_pattern(arg1):
                player_args |=  {"brightness_pattern": arg2}
            else:
                return False
        else:
            player_args |= {"brightness_pattern": "AAAAAAAAAA"}
    elif arg1 in player.mode_id_to_index:
        player_args = {"mode_index": player.mode_id_to_index[arg1]}
    else:
        return False
    return player_args

def main():
    """Execute Marquee application."""
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
