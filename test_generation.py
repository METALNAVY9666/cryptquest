"""test de la génération des niveaux"""
from typing import List, Any
import math

import pygame

pygame.init()

POLICE = pygame.font.SysFont('Arial', 20)


def sequence(entree: List[int]):
    a_ret: List[int] = []
    for numn in range(1, len(entree) + 1):
        res = 0
        for numk, elm in enumerate(entree[:numn]):
            res += elm * math.comb(numn - 1, numk)
        a_ret.append(res)
    return a_ret


def operation(entree: int, mult: int, div: int):
    return mult * entree + 1 if entree % div else entree // div


def sequence2(depart: int, quantite: int, mult: int, div: int):
    a_ret = [hex(depart)[2:]]

    for _ in range(quantite):
        a_ret.append(hex(operation(int(a_ret[-1], 16), mult, div))[2:])
    return a_ret


ls = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
      'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
      'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


def sequence3(entree: str, mult: int, offset: int):
    res: str = ""
    for lettre in entree:
        res += chr(ord('a') + (mult * (ord(lettre) - ord('a')) + offset) % 26)

    return res


def forme(sequence: List[Any]):
    carre = pygame.Surface((30, 30), pygame.SRCALPHA)
    carre_rect = carre.get_rect()

    surface = pygame.Surface((len(sequence) * 30, 30))

    for posx, elm in enumerate(sequence):
        surf = carre.copy()

        surf_elm = POLICE.render(str(elm), True, '#FFFFFF')
        rect = surf_elm.get_rect()
        rect.center = carre_rect.center

        surf.blit(surf_elm, rect)
        surface.blit(surf, (posx * 30, 0))
    
    return surface



WINDOW = pygame.display.set_mode((600, 600))
surf = forme(sequence2(27, 8, 3, 2))
rect = surf.get_rect()
rect.center = WINDOW.get_rect().center

while True:
    WINDOW.fill('#000000')

    WINDOW.blit(surf, rect)
    pygame.display.flip()

