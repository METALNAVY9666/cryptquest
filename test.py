from typing import Callable
import pygame

pygame.init()

def depy(t: float):
    return min((200 * t**2 - 400*t + 500), 500)

def depx(t: float):
    return (40 * t if t < 3 else 120) + 50

def rot(t: float):
    return -120 * t if t < 3 else 0

def appel(fnct: Callable[[float], float], t: float):
    print(t / 1000)
    return fnct(t / 1000)

WINDOW = pygame.display.set_mode((600, 600))
backup = WINDOW.copy()

carre = pygame.Surface((30, 30), pygame.SRCALPHA)
carre.fill('#FFFFFF')



time = pygame.time.get_ticks()
start_time = time

while True:
    # clear
    WINDOW.blit(backup, (0, 0))

    time = pygame.time.get_ticks() - start_time

    image = pygame.transform.rotate(carre, appel(rot, time))
    rect = image.get_rect()
    rect.center = round(appel(depx, time)), round(appel(depy, time))

    WINDOW.blit(image, rect)

    pygame.display.flip()