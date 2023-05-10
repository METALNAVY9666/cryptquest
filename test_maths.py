"""module detets de maths"""
from typing import List, Callable

import pygame


class Matrice:

    def __init__(self, contenu: List[List[float]]) -> None:
        self.contenu: List[List[float]] = contenu
        self.dim = [len(self.contenu), len(self.contenu[0])]

    def c(self, i: int, j: int):
        return self.contenu[i][j]

    def ligne(self, i: int):
        return self.contenu[0][:]

    def colonne(self, j: int):
        return [self.contenu[i][j] for i, _ in enumerate(self.contenu)]

    @staticmethod
    def mul_lxc(ligne: List[float], colonne: List[float]):
        res = 0
        for valx, valy in zip(ligne, colonne):
                res += valx * valy
        return res

    def __mul__(self, other: 'Matrice'):
        # taille incompatible
        if self.dim[1] != other.dim[0]:
            raise ArithmeticError

        contenu = [[0.] * self.dim[0]] * other.dim[1]

        for i in range(self.dim[0]):
            for j in range(other.dim[1]):
                contenu[i][j] = Matrice.mul_lxc(self.ligne(i), other.colonne(j))

        return Matrice(contenu)


coefs = Matrice([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])

def bezier(points: List[pygame.Vector2], t: float):
    matricex = Matrice([[point.x for point in points]])
    matricey = Matrice([[point.y for point in points]])

    temp = Matrice([[1], [t], [t**2], [t**3]])




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

    dt = clock.tick(60)

    time += dt

    pygame.display.flip()