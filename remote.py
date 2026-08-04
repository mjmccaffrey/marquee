import pygame
import time

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Keypress Example")
# clock = pygame.Clock()
while True:
    time.sleep(0.01)
    for i, e in enumerate(pygame.event.get()):
        if e.type == pygame.KEYDOWN:
            match e.key:
                case pygame.K_RIGHT:
                    print('right')
                case pygame.K_LEFT:
                    print('left')
                case _:
                    print(i, e)
