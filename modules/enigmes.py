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

    def generate_solution(self) -> Any:
        """génère la solution"""
        ...

    def generate(self) -> List[Any]:
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

    def generate_solution(self) -> float:
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


shape1 = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.rect(shape1, '#FFFFFF', pygame.Rect(5, 5, 40, 40))

shape2 = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.circle(shape2, '#FFFFFF', (25, 25), 24)

shape3 = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.polygon(shape3, '#FFFFFF', [(37, 3), (0, 25), (37, 47)])

shape4 = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.polygon(shape4, '#FFFFFF', [(20, 0), (30, 0), (30, 50), (20, 50)])


vert = pygame.Surface((50, 50), pygame.SRCALPHA)
vert.fill('#20E040')

rouge = pygame.Surface((50, 50), pygame.SRCALPHA)
rouge.fill('#E00030')

orange = pygame.Surface((50, 50), pygame.SRCALPHA)
orange.fill('#E06000')


class GeometricCombinaison:
    """représentation des combinaisons géométriques"""

    shapes: List[pygame.Surface] = [shape1, shape2, shape3, shape4]
    remplissage: List[pygame.Surface] = [vert, rouge, orange]

    def __init__(self, coefficients: List[Tuple[int, int, int]]) -> None:
        self.coefficients = coefficients

    @staticmethod
    def scale(surface: pygame.Surface, echelle: int):
        """condense la surface avec un facteur sqrt(2)^(-n)"""
        return pygame.transform.scale_by(surface, 1 / (math.sqrt(2) ** echelle))

    @staticmethod
    def transparent(surface: pygame.Surface, couleur: Tuple[int, int, int, int]):
        """rend transparent tous les pixels de la couleur donnée"""
        transparent_mask = pygame.mask.from_threshold(
            surface, couleur, (1, 1, 1, 1))
        surface_mask = pygame.mask.from_surface(surface)
        surface_mask.erase(transparent_mask, (0, 0))

        return surface_mask.to_surface(surface=pygame.Surface(surface_mask.get_size(), pygame.SRCALPHA),
                                       setsurface=surface, unsetcolor=None)

    def get_surface(self):
        """forme la surface à partir des coefficients"""
        surface: pygame.Surface = pygame.Surface((0, 0))

        for ind, tpl in enumerate(self.coefficients):
            surf = self.intersect(GeometricCombinaison.shapes[tpl[0]],
                                  GeometricCombinaison.remplissage[tpl[1]])
            surf = pygame.transform.rotate(surf, tpl[2] * 90)
            if surface.get_width() == 0:
                surface = surf
            else:
                surf = self.scale(surf, ind)

                # on centre l'image
                sizex = int((surface.get_width() - surf.get_width()) / 2)
                sizey = int((surface.get_height() - surf.get_height()) / 2)

                surface.blit(surf, (sizex, sizey))

        surface = self.transparent(surface, (0, 0, 0, 255))

        return surface

    @staticmethod
    def intersect(shape: pygame.Surface, remplissage: pygame.Surface):
        """intersection"""
        mask1 = pygame.mask.from_surface(shape)
        mask2 = pygame.mask.from_surface(remplissage)

        intersection = mask1.overlap_mask(mask2, (0, 0))

        return intersection.to_surface(surface=pygame.Surface(intersection.get_size(), pygame.SRCALPHA),
                                       setsurface=remplissage, unsetcolor=None)


class GeometricEnigme(EnigmeGenerateur):
    """génération d'énigme géométrique"""

    difficulte_ind = ['simple', 'intermediaire', 'difficile']

    def __init__(self, size: int) -> None:
        self.shape_variation = [random.randint(0, len(GeometricCombinaison.shapes) - 1),
                                random.randint(0, len(GeometricCombinaison.shapes) - 1)]

        self.filling_variation = [random.randint(0, len(GeometricCombinaison.remplissage) - 1),
                                  random.randint(0, len(GeometricCombinaison.remplissage) - 1)]

        self.rotation_variation = [random.randint(-1, 1), random.randint(-1, 1)]

        self.valeur_initiales: List[Tuple[int, int, int]] = []

        for _ in range(3):
            self.valeur_initiales.append((random.randint(0, len(GeometricCombinaison.shapes) - 1),
                                  random.randint(
                                      0, len(GeometricCombinaison.remplissage) - 1),
                                  random.randint(0, 3)))

        self.size = size

        print(self.shape_variation, self.filling_variation, self.rotation_variation)

    @classmethod
    def create(cls) -> EnigmeGenerateur:
        return cls(cls.difficulte_ind.index(DIFFICULTE_NV) + 2)

    def generate(self) -> List[List[Tuple[int, int, int]]]:
        """génère l'énigme"""
        res: List[List[Tuple[int, int, int]]] = []
        # à remettre bien
        for ind in range(self.size ** 2):
            coefficients: List[Tuple[int, int, int]] = []

            for indx in range(3):
                new_shape = (self.valeur_initiales[indx][0] + self.shape_variation[0] * (ind % self.size)
                             + self.shape_variation[1] * (ind // self.size)) % len(GeometricCombinaison.shapes)
                new_remplissage = (self.valeur_initiales[indx][1] + self.filling_variation[0] * (ind % self.size)
                                   + self.filling_variation[1] * (ind // self.size)) % len(GeometricCombinaison.remplissage)
                new_rotation = (self.valeur_initiales[indx][2] + self.rotation_variation[0] * (ind % self.size)
                                + self.rotation_variation[1] * (ind // self.size)) % 4

                coefficients.append((new_shape, new_remplissage, new_rotation))
            res.append(coefficients)
        return res

    def generate_solution(self) -> List[Tuple[int, int, int]]:
        """génère la solution"""
        coefficients: List[Tuple[int, int, int]] = []

        for indx in range(3):
            new_shape = (self.valeur_initiales[indx][0] + self.shape_variation[0] * ((self.size ** 2 - 1)
                                                                                     % self.size)
                         + self.shape_variation[1] * ((self.size ** 2 - 1) // self.size)) % len(GeometricCombinaison.shapes)
            new_remplissage = (self.valeur_initiales[indx][0] + self.filling_variation[0] *
                               ((self.size ** 2 - 1) % self.size)
                               + self.filling_variation[1] * ((self.size ** 2 - 1) // self.size)) % len(GeometricCombinaison.remplissage)
            new_rotation = (self.valeur_initiales[indx][0] + self.rotation_variation[0] *
                            ((self.size ** 2 - 1) % self.size)
                            + self.rotation_variation[1] * ((self.size ** 2 - 1) // self.size)) % 4

            coefficients.append((new_shape, new_remplissage, new_rotation))
        return coefficients


class Enigme:
    """classe de gestion des énigmes"""

    current_enigme: 'None | Enigme' = None

    def __init__(self, generateur: EnigmeGenerateur, interface_nom: str) -> None:
        self.serie = generateur.generate()
        self.solution = generateur.generate_solution()
        print(self.serie)
        print(self.solution)
        self.pos = RelativePos(0.5, 0.5, 1)

        match generateur:
            case GeometricEnigme():
                surface = self.tableau_to_surface(self.serie, generateur.size, 300)
            case _:
                surface = self.liste_to_surface(self.serie)

        self.element = StaticElement(
            self, surface, interface_nom)

        #  à retirer
        lie(lambda **_: print('hi'), 'enigme_resolu')
        #self.essaie(self.solution)

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

    @staticmethod
    def tableau_to_surface(tableau: List[List[Tuple[int, int, int]]], nombre: int, taille_surface: int):
        """transforme un tableau carré 2d de taille donnée en surface"""
        offset = 10
        surface = pygame.Surface((taille_surface + (nombre - 1) * offset,
                                  taille_surface + (nombre - 1) * offset))
        unite = taille_surface / nombre
        for ind, valeur in enumerate(tableau):
            surf = GeometricCombinaison(valeur).get_surface()

            # ajuste la taille de la surface si nécessaire
            if abs(surf.get_width() - unite) > 2:
                surf = pygame.transform.scale(surf, (unite, unite))

            surface.blit(surf, ((unite + offset) * (ind % nombre),
                         (unite + offset) * (ind // nombre)))
        return surface

    @classmethod
    def create(cls, generateur: EnigmeGenerateur):
        cls.current_enigme = cls(generateur.create(), 'game')
