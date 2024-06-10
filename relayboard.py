## Marquee Lighted Sign Project - relayboard

# !!!!!!!!!!! make and model of board

""" """
import serial

class RelayBoard():
    """ """

    def __init__(self):
        """ """
        self._relay_board = serial.Serial("/dev/ttyACM0")

    def set_relays(self, relay_pattern_hex):
        """ """
        command = f"relay writeall {relay_pattern_hex}\n\r"
        self._relay_board.write(bytes(command, 'utf-8'))

    def make_pylint_happier(self):
        """2nd public method."""
