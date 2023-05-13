"""module de gestion des énigmes"""

from abc import ABC
from typing import List, Dict, Any, Tuple
import random
import math
import json

import pygame

from modules.graphics import StaticElement, POLICE, RelativePos
from modules.outils import appel, lie


with open('ressources/data/difficulte.json', 'r', encoding='utf-8') as file:
    DIFFICULTE_DCT = json.load(file)

DIFFICULTE_NV: str = 'simple'


def extract(parametre: str, typ: str):
    """
    extrait le minimum et le maximum d'une
    clef dans le dictionnaire de difficulté
    """
    # raise KeyError volontaire si la clef n'existe pas
    return (DIFFICULTE_DCT[DIFFICULTE_NV][typ][parametre]['min'],
            DIFFICULTE_DCT[DIFFICULTE_NV][typ][parametre]['max'])


class EnigmeGenerateur(ABC):
    """génération des énigmes"""

    def __init__(self) -> None:
        self.parametre: Dict[str, Any]
        self.quantite: int

    def generate_solution(self) -> str | float:
        """génère la solution"""
        ...

    def generate(self) -> List[str] | List[float]:
        """génère une séquence"""
        ...

    @classmethod
    def create(cls) -> 'EnigmeGenerateur':
        """crée une instance du générateur selon la difficulté"""
        ...


class BinomialEnigme(EnigmeGenerateur):
    """génération d'énigme binomiale"""

    def __init__(self, profondeur: int, quantite: int) -> None:
        self.quantite = quantite
        self.profondeur = profondeur
        self.parametre = {'entree': [
            random.randint(-7, 7) for _ in range(profondeur)]}

    def generate_solution(self) -> str | float:
        """génère la solution"""
        return self.sequence(self.parametre['entree'] + [0] * (self.quantite - self.profondeur + 1))[-1]

    @staticmethod
    def sequence(entree: List[int]):
        """génère la séquence à partir de l'entrée"""
        a_ret: List[float] = []
        for numn in range(1, len(entree) + 1):
            res = 0
            for numk, elm in enumerate(entree[:numn]):
                res += elm * math.comb(numn - 1, numk)
            a_ret.append(res)
        return a_ret

    def generate(self) -> List[float]:
        """génère la séquence de l'énigme"""
        return self.sequence(self.parametre['entree'] + [0] * (self.quantite - self.profondeur))

    @classmethod
    def create(cls) -> 'BinomialEnigme':
        """crée une instance BinomialeEnigme"""
        profondeur = random.randint(*extract('profondeur', 'binomiale'))
        quantite = random.randint(*extract('quantite', 'binomiale'))

        return BinomialEnigme(profondeur, quantite)


class SequentialEnigme(EnigmeGenerateur):
    """génération d'énigme séquentielle"""

    def __init__(self, quantite: int, mult: int, depart: int) -> None:
        self.parametre = {'depart': depart, 'quantite': quantite,
                          'mult': 2 * mult + 1, 'div': 2}
        self.last_value: int

    @staticmethod
    def sequence(depart: int, quantite: int, mult: int, div: int) -> List[int]:
        """génère la séquence à partir de l'entrée"""
        a_ret = [depart]

        for _ in range(quantite):
            a_ret.append(SequentialEnigme.operation(a_ret[-1], mult, div))

        return a_ret

    @staticmethod
    def operation(entree: int, mult: int, div: int):
        """réalise l'opération d'itération de la suite"""
        return mult * entree + 1 if entree % div else entree // div

    def generate(self) -> List[str]:
        """génère la séquence de l'énigme"""
        seq = self.sequence(**self.parametre)
        self.last_value = seq[-1]

        return [hex(valeur)[2:] for valeur in seq]

    def generate_solution(self) -> str:
        """génère la solution"""
        return hex(SequentialEnigme.operation(self.last_value, self.parametre['mult'],
                                              self.parametre['div']))[2:]

    @classmethod
    def create(cls) -> 'SequentialEnigme':
        """crée une instance de cette classe en fonction de la difficulté"""
        quantite = random.randint(*extract('quantite', 'sequence'))
        mult = random.randint(*extract('multiplication', 'sequence'))
        depart = random.randint(*extract('depart', 'sequence'))

        return SequentialEnigme(quantite, mult, depart)
    

# à changer


shape1 = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.rect(shape1, '#FFFFFF', pygame.Rect(5, 5, 20, 20))

shape2 = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.circle(shape2, '#FFFFFF', (15, 15), 9)

shape3 = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.polygon(shape3, '#FFFFFF', [(5, 5), (15, 25), (25, 5)])

shape4 = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.polygon(shape4, '#FFFFFF', [(10, 0), (20, 0), (20, 30), (10, 30)])


raye = pygame.Surface((30, 30), pygame.SRCALPHA)

for x in range(30):
    for y in range(30):
        if not (x + y) % 3:
            raye.set_at((x, y), "#FF00FF")

vide = pygame.Surface((30, 30), pygame.SRCALPHA)
vide.fill('#000000')

plein = pygame.Surface((30, 30), pygame.SRCALPHA)
plein.fill('#00FF00')


class GeometricCombinaison:
    """représentation des combinaisons géométriques"""

    shapes: List[pygame.Surface] = [shape1, shape2, shape3, shape4]
    remplissage: List[pygame.Surface] = [raye, vide, plein]

    def __init__(self, coefficients: List[Tuple[int, int, int]]) -> None:
        self.coefficients = coefficients

    @staticmethod
    def scale(surface: pygame.Surface, echelle: int):
        """condense la surface avec un facteur sqrt(2)^(-n)"""
        back = pygame.Surface(surface.get_size())
        back_rect = back.get_rect()
        surf = pygame.transform.scale_by(surface, 1 / (math.sqrt(2) ** echelle))
        rect = surf.get_rect()
        rect.center = back_rect.center

        back.blit(surf, rect)
        return back

    def get_surface(self):
        """forme la surface à partir des coefficients"""
        surface: None | pygame.Surface = None

        for ind, tpl in enumerate(self.coefficients):
            surf = self.intersect(GeometricCombinaison.shapes[tpl[0]],
                                  GeometricCombinaison.remplissage[tpl[1]])
            surf = pygame.transform.rotate(surf, ind * tpl[2] * 90)
            if surface is None:
                surface = surf
            else:
                surf = self.scale(surf, ind)
                surface.blit(surf, (0, 0))

    @staticmethod
    def intersect(shape: pygame.Surface, remplissage: pygame.Surface):
        """intersection"""
        mask1 = pygame.mask.from_surface(shape)
        mask2 = pygame.mask.from_surface(remplissage)

        intersection = mask1.overlap_mask(mask2, (0, 0))

        return intersection.to_surface(surface=pygame.Surface(intersection.get_size(), pygame.SRCALPHA),
                                       setsurface=remplissage, unsetcolor=None)


class GeometricEnigme:
    """génération d'énigme géométrique"""

    def __init__(self) -> None:
        pass


class Enigme:
    """classe de gestion des énigmes"""

    current_enigme: 'None | Enigme' = None

    def __init__(self, generateur: EnigmeGenerateur, interface_nom: str) -> None:
        self.serie = generateur.generate()
        self.solution = generateur.generate_solution()
        self.pos = RelativePos(0.5, 0.5, 1)

        self.element = StaticElement(
            self, self.liste_to_surface(self.serie), interface_nom)

        #  à retirer
        lie(lambda **_: print('hi'), 'enigme_resolu')
        self.essaie(self.solution)

    def essaie(self, valeur: str | float) -> bool:
        """vérifie si la solution donnée est la bonne:
        si la valeur est correcte, trigger l'événement donné
        et supprime l'énigme"""

        if not valeur == self.solution:
            return False

        appel('enigme_resolu', {})
        self.element.destroy()
        Enigme.current_enigme = None

        return True

    @staticmethod
    def liste_to_surface(sequence: List[str] | List[float]):
        """transforme une liste en surface"""
        size = 50
        carre = pygame.Surface((size, size), pygame.SRCALPHA)
        carre_rect = carre.get_rect()

        surface = pygame.Surface((len(sequence) * size, size))

        for posx, elm in enumerate(sequence):
            surf = carre.copy()

            surf_elm = POLICE.render(str(elm), True, '#FFFFFF')
            rect = surf_elm.get_rect()
            rect.center = carre_rect.center

            surf.blit(surf_elm, rect)
            surface.blit(surf, (posx * size, 0))

        return surface

    @classmethod
    def create(cls, generateur: EnigmeGenerateur):
        cls.current_enigme = cls(generateur.create(), 'game')
