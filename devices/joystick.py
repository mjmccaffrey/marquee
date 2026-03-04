# """Marquee Lighted Sign Project - joystick"""

# from dataclasses import dataclass
# from enum import Enum

# from gpiozero import Button as _Button  # type: ignore


# class Directions(Enum):
#     """"""
#     UP = 0
#     DOWN = 1
#     LEFT = 2
#     RIGHT = 3
#     UPRIGHT = 4
#     UPLEFT = 5
#     DOWNRIGHT = 6
#     DOWNLEFT = 7


# @dataclass
# class Joystick:
#     """"""
#     up_switch: _Button
#     down_switch: _Button
#     left_switch: _Button
#     right_switch: _Button

#     D = Directions
#     def update(self):
#         match state:
#             case '0000':
#                 dir = None
#             case '0001':
#                 dir = D.LEFT
#             case '0010':
#                 dir = D.RIGHT
#             case '0100':
#                 dir = D.DOWN
#             case '0101':
#                 dir = D.DOWNLEFT
#             case '0110':
#                 dir = D.DOWNRIGHT
#             case '1000':
#                 dir = D.UP
#             case '1001':
#                 dir = D.UPLEFT
#             case '1010':
#                 dir = D.UPRIGHT
#             case _:
#                 raise ValueError(state)
