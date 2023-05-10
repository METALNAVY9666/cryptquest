from typing import Callable
import pygame

pygame.init()


def depy(t: float):
    return min((200 * (t % 4) **2 - 400* (t % 4) + 500), 500)

def depx(t: float):
    return (80 * (t % 4) + t // 4 * 160 if t % 4 < 2 else (t // 4 + 1) * 160) + 50

def rot(t: float):
    return -180 * t if t % 4 < 2 else 0

def appel(fnct: Callable[[float], float], t: float):
    print(t)
    return fnct(t / 1000)

WINDOW = pygame.display.set_mode((600, 600))
backup = WINDOW.copy()

carre = pygame.Surface((30, 30), pygame.SRCALPHA)
carre.fill('#FFFFFF')

clock = pygame.time.Clock()
time = 0

while True:
    # clear
    WINDOW.blit(backup, (0, 0))

    image = pygame.transform.rotate(carre, appel(rot, time))
    rect = image.get_rect()
    rect.center = round(appel(depx, time)), round(appel(depy, time))

    WINDOW.blit(image, rect)

    dt = clock.tick(60)

    time += dt

    pygame.display.flip()