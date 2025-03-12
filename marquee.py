"""Marquee Lighted Sign Project - main"""

from arguments import display_help, process_arguments
from modes import register_modes
from players import Player

def main():
    """Execute Marquee application."""
    print("Executing Marquee")
    try:
        player = Player()
        register_modes(player)
        if arg := process_arguments(player):
            assert isinstance(arg, dict)
            player.execute(**arg)
        else:
            display_help(player)
    finally:
        try:
            player.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
