"""module detets de maths"""
from typing import List, Any, Iterable, Tuple

import pygame


class Matrice:

    def __init__(self, contenu: List[List[float]]) -> None:
        self.contenu: List[List[float]] = contenu
        self.dim = [len(self.contenu), len(self.contenu[0])]

    def c(self, i: int, j: int):
        return self.contenu[i][j]

    def ligne(self, i: int):
        return self.contenu[i][:]

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

        contenu = [[0.] * other.dim[1]] * self.dim[0]

        for i in range(self.dim[0]):
            for j in range(other.dim[1]):
                contenu[i][j] = Matrice.mul_lxc(self.ligne(i), other.colonne(j))

        return Matrice(contenu)

    def __str__(self):
        cdc = ''
        for i in range(self.dim[0]):
            if i == 0:
                cdc += "\u23A1"
            elif i == self.dim[0] - 1:
                cdc += "\u23A3"
            else:
                cdc += "\u23A2"

            cdc += " , ".join([str(val) for val in self.ligne(i)])

            if i == 0:
                cdc += "\u23A4"
            elif i == self.dim[0] - 1:
                cdc += "\u23A6"
            else:
                cdc += "\u23A2"
            
            cdc += "\n"

        return cdc


coefs = Matrice([[1, 0, -3, 3], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])

points: List[pygame.Vector2] = [pygame.Vector2(100, 100), pygame.Vector2(300, 100),
                                      pygame.Vector2(200, 0), pygame.Vector2(300, 200)]

matrice_x = Matrice([[point.x for point in points]])
matrice_y = Matrice([[point.y for point in points]])

pre_compute_x = matrice_x * coefs
pre_compute_y = matrice_y * coefs

def bezier(pre_compute_matrices: Tuple[Matrice, Matrice], temps: float, max_temps: int):
    temps /= max_temps

    matrice_temps = Matrice([[1], [temps], [temps**2], [temps**3]])

    posx = pre_compute_matrices[0] * matrice_temps
    posy = pre_compute_matrices[1] * matrice_temps

    return posx.c(0, 0), posy.c(0, 0)


def round_tuple(tpl: Iterable[Any]):
    """arrondi un tuple"""
    return tuple(round(val) for val in tpl)


WINDOW = pygame.display.set_mode((600, 600))
backup = WINDOW.copy()

carre = pygame.Surface((30, 30), pygame.SRCALPHA)
carre.fill('#FFFFFF')

rect = carre.get_rect()

clock = pygame.time.Clock()
time = 0

while True:
    # clear
    WINDOW.blit(backup, (0, 0))
    
    rect.center = round_tuple(bezier((pre_compute_x, pre_compute_y), time / 1000, 5))
    
    WINDOW.blit(carre, rect)

    dt = clock.tick(60)

    time += dt

    pygame.display.flip()