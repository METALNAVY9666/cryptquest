"""module de gestion des énigmes"""

from abc import ABC
from typing import List, Dict, Any, Tuple, Callable, Set
import random
import math
import json

import pygame

from modules.graphics import (StaticElement, RelativePos, Draggable,
                              Vector3, Frame, Interface, StaticModel, absolute_to_relpos,
                              Bouton, Texte)
from modules.outils import appel, lie, vide, delie

# chargement

with open('ressources/data/difficulte.json', 'r', encoding='utf-8') as file:
    DIFFICULTE_DCT = json.load(file)

DIFFICULTE_NV: str = 'intermediaire'

DCT_SURFACE: Dict[str, pygame.Surface] = {}

DCT_SURFACE['carre'] = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.rect(DCT_SURFACE['carre'], '#FFFFFF', pygame.Rect(5, 5, 40, 40))

DCT_SURFACE['disque'] = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.circle(DCT_SURFACE['disque'], '#FFFFFF', (25, 25), 24)

DCT_SURFACE['triangle'] = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.polygon(DCT_SURFACE['triangle'], '#FFFFFF', [
                    (37, 3), (0, 25), (37, 47)])

DCT_SURFACE['rectangle'] = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.polygon(DCT_SURFACE['rectangle'], '#FFFFFF', [
                    (20, 0), (30, 0), (30, 50), (20, 50)])


POLICE = pygame.font.SysFont('Arial', 30)


vert = pygame.Surface((50, 50), pygame.SRCALPHA)
vert.fill('#20E040')

rouge = pygame.Surface((50, 50), pygame.SRCALPHA)
rouge.fill('#E00030')

orange = pygame.Surface((50, 50), pygame.SRCALPHA)
orange.fill('#E06000')


# fonctions & classes


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

    def generate_solution(self) -> str:
        """génère la solution"""
        return str(self.sequence(self.parametre['entree'] + [0] * (self.quantite - self.profondeur + 1))[-1])

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


class GeometricCombinaison:
    """représentation des combinaisons géométriques"""

    shapes: List[pygame.Surface] = [DCT_SURFACE['carre'],
                                    DCT_SURFACE['disque'], DCT_SURFACE['triangle'], DCT_SURFACE['rectangle']]
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
            if GeometricCombinaison.shapes[tpl[0]] not in (DCT_SURFACE['carre'], DCT_SURFACE['disque']):
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

    difficulte_ind = ['difficile', 'intermediaire', 'simple']

    def __init__(self, size: int) -> None:
        self.shape_variation = [random.randint(0, len(GeometricCombinaison.shapes) - 1),
                                random.randint(0, len(GeometricCombinaison.shapes) - 1)]

        self.filling_variation = [random.randint(0, len(GeometricCombinaison.remplissage) - 1),
                                  random.randint(0, len(GeometricCombinaison.remplissage) - 1)]

        self.rotation_variation = [
            random.randint(-1, 1), random.randint(-1, 1)]

        self.valeur_initiales: List[Tuple[int, int, int]] = []

        for _ in range(3):
            self.valeur_initiales.append((random.randint(0, len(GeometricCombinaison.shapes) - 1),
                                          random.randint(
                0, len(GeometricCombinaison.remplissage) - 1),
                random.randint(0, 3)))

        self.size = size

    @classmethod
    def create(cls) -> EnigmeGenerateur:
        return cls(cls.difficulte_ind.index(DIFFICULTE_NV) + 2)

    def generate(self) -> List[List[Tuple[int, int, int]]]:
        """génère l'énigme"""
        res: List[List[Tuple[int, int, int]]] = []
        # à remettre bien
        for ind in range(self.size ** 2 - 1):
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

    def calcule_solution(self) -> List[List[int]]:
        """calcule la solution"""
        coefficients: List[List[int]] = []

        for indx in range(3):
            shape = (self.valeur_initiales[indx][0] + self.shape_variation[0] * ((self.size ** 2 - 1)
                                                                                     % self.size)
                         + self.shape_variation[1] * ((self.size ** 2 - 1)
                                                      // self.size)) % len(GeometricCombinaison.shapes)
            remplissage = (self.valeur_initiales[indx][1] + self.filling_variation[0] *
                               ((self.size ** 2 - 1) % self.size)
                               + self.filling_variation[1] *
                               ((self.size **2 - 1) // self.size)) % len(GeometricCombinaison.remplissage)

            rotation = (self.valeur_initiales[indx][2] + self.rotation_variation[0] *
                            ((self.size ** 2 - 1) % self.size)
                            + self.rotation_variation[1] * ((self.size ** 2 - 1) // self.size)) % 4

            coefficients.append([shape, remplissage, rotation])
        return coefficients
    
    def filtre(self, solution: List[List[int]]) -> List[List[int]]:
        """filtre les solutions selon leur faisabilité"""
        new_solution: List[List[int]] = []
        for indice, elm in enumerate(solution):
            shape, remplissage, rotation = elm

            new_shape: int = shape
            new_remplissage: int = remplissage
            new_rotation: int = rotation

            # remplissage

            if ((indice > 0 and solution[indice - 1][1] == remplissage
                 and shape < 3 and solution[indice - 1][0] < 2)):
                new_shape = 0
                new_rotation = 0

            # rotation
            elif shape < 2:
                new_rotation = 0
            elif shape == 2:
                new_rotation = rotation
            else:
                new_rotation = rotation % 2

            new_solution.append([new_shape, new_remplissage, new_rotation])

        return new_solution

    def generate_solution(self) -> List[List[int]]:
        """génère la solution"""
        solution = self.calcule_solution()
        return self.filtre(solution)


class Enigme:
    """classe de gestion graphique des énigmes"""

    current_enigme: 'None | Enigme' = None

    def __init__(self, generateur: EnigmeGenerateur, sequence_to_frame: Callable[[Any], Frame]) -> None:
        self.serie = generateur.generate()
        self.solution = generateur.generate_solution()

        self.frame = sequence_to_frame(self.serie)

        lie(self.essaie, 'essaie')

    def essaie(self, valeur: Any) -> bool:
        """vérifie si la solution donnée est la bonne:
        si la valeur est correcte, trigger l'événement donné
        et supprime l'énigme"""

        if not valeur == self.solution:
            return False

        vide('essaie')
        appel('enigme_resolu', {})
        self.frame.destroy()
        Enigme.current_enigme = None

        return True

    @classmethod
    def create(cls, generateur: EnigmeGenerateur, sequence_to_frame: Callable[[Any], Frame]):
        cls.current_enigme = cls(generateur.create(), sequence_to_frame)


def tableau_to_frame(tableau: List[List[Tuple[int, int, int]]]):
    """transforme un tableau carré 2d de taille donnée en surface"""
    nombre = round((len(tableau) + 1) ** 0.5)
    offset = 30

    taille_surface = 373

    interface_enigme = Interface("enigme")

    background = DCT_SURFACE['background_geometrique']
    unite = (taille_surface - offset) / nombre - offset

    for ind, valeur in enumerate(tableau):
        surf = GeometricCombinaison(valeur).get_surface()

        # ajuste la taille de la surface si nécessaire
        if abs(surf.get_width() - unite) > 2:
            surf = pygame.transform.scale(surf, (unite, unite))

        StaticModel(surf, Vector3(389 + (unite + offset) * (ind % nombre) + offset,
                                  42 + (unite + offset) * (ind // nombre) + offset, 1),
                    'enigme')

    # on ajoute la zone de solution
    DropZone(Vector3(389 + (unite + offset) * ((len(tableau)) % nombre),
                     42 + (unite + offset) * ((len(tableau)) // nombre), 1), unite, 'enigme')

    # on ajoute les éléments de solution
    Brique(Vector3(32 + 71, 32 + 96, 2, 'centre'), unite, 'enigme')
    Brique(Vector3(32 + 71, 32 + 192, 2, 'centre'), unite, 'enigme')
    Brique(Vector3(32 + 71, 32 + 288, 2, 'centre'), unite, 'enigme')

    return Frame('enigme', interface_enigme, background, RelativePos(0.5, 0.5, 1), 'game')


def liste_to_frame(sequence: List[str | float]):
    """transforme une liste en surface"""
    # on ajoute le point d'interrogation pour l'esthétique
    sequence.append("?")

    taille_surface = 380
    offset = 10
    nombre = len(sequence)

    background = DCT_SURFACE['background_numerique']
    interface_enigme = Interface('enigme')

    unite = (taille_surface - offset) / nombre - offset

    for indice, elm in enumerate(sequence):
        zone_carre = pygame.Surface((round(unite), round(unite)), pygame.SRCALPHA)
        zone_carre_rect = zone_carre.get_rect()
        surf_elm = POLICE.render(str(elm), True, '#FFFFFF')
        rect = surf_elm.get_rect()
        rect.center = zone_carre_rect.center

        zone_carre.blit(surf_elm, rect)

        StaticModel(zone_carre, Vector3(644, 34 + offset + (offset + unite) * indice, 1, 'top'), 'enigme')

    # ajout des boutons

    texte_reponse = Texte(Vector3(224, 79, 1, 'centre'), POLICE, '#000000', interface_nom='enigme')
    Bouton(Vector3(351, 351, 1), pygame.Surface((48, 48), pygame.SRCALPHA),
           lambda: appel('essaie', {'valeur': texte_reponse.texte}), 'enigme')
    
    Bouton(Vector3(351, 293, 1), pygame.Surface((48, 48), pygame.SRCALPHA),
           lambda: setattr(texte_reponse, 'texte', ''), 'enigme')
    
    # boutons de 0 à F
    for value in range(16):
        Bouton(Vector3(111 + (50 + 8) * (value % 4), 350 - (50 + 8) * (value // 4), 1),
               pygame.Surface((50, 50), pygame.SRCALPHA), texte_reponse.ajoute_lettre,
               'enigme', data = {'lettre': hex(value)[2:]})

    return Frame('enigme', interface_enigme, background, RelativePos(0.5, 0.5, 1), 'game')


class Brique(Draggable):
    """classe de gestion de brique élémentaire géométrique"""

    briques: Set['Brique'] = set()

    def __init__(self, pos: Vector3, size: int, interface_nom: str,
                 composant: List[List[int]] | None = None) -> None:
        super().__init__(pos, pygame.Surface((0, 0)), interface_nom)
        self.size = size
        self.interface_nom = interface_nom
        self.coefficient = composant if composant is not None else [[0, 0, 0]]
        self.freeze = False

        Brique.briques.add(self)
        lie(self.reset, 'reset')

    def destroy(self):
        """détruit la brique"""
        delie(self.reset, 'reset')
        self.element.destroy()
        Brique.briques.remove(self)

    def reset(self):
        """réinitialise la brique"""
        for num, composant in enumerate(self.coefficient):
            Brique(Vector3(32 + 71, 32 + 96 * (num + 1), 2, 'centre'), self.size,
                   self.interface_nom, [composant[:]])  # type: ignore
        self.destroy()

    def on_keypress(self, event: pygame.event.Event):
        """gestion de touches"""
        if not self.freeze and self.element.elm_infos['rect'].collidepoint(absolute_to_relpos(
                Vector3(*pygame.mouse.get_pos(), 0))):
            match event.key:
                case pygame.K_s:
                    self.coefficient[0][0] += 1
                    self.coefficient[0][0] %= 4
                case pygame.K_c:
                    self.coefficient[0][1] += 1
                    self.coefficient[0][1] %= 3
                case pygame.K_r:
                    if self.coefficient[0][0] < 2:
                        return
                    self.coefficient[0][2] += 1
                    if self.coefficient[0][0] == 2:
                        self.coefficient[0][2] %= 4
                    else:
                        self.coefficient[0][2] %= 2
                case _:
                    ...

    def on_declick(self, event: pygame.event.Event):
        super().on_declick(event)
        self.stack()

    def stack(self):
        """fusionne deux figures"""
        # on ne fusionne pas tant qu'on bouge
        if self.state:
            return

        a_detruire: List['Brique'] = []
        for elm in Brique.briques:
            if (elm != self and not elm.state and
                    self.element.elm_infos['rect'].colliderect(elm.element.elm_infos['rect'])):
                self.freeze = True
                self.coefficient = elm.coefficient + self.coefficient
                a_detruire.append(elm)

        while len(a_detruire):
            a_detruire.pop(0).destroy()

    def update(self):
        """fonction de mise à jour"""
        self.element.elm_infos['surface'] = pygame.transform.scale(GeometricCombinaison(
            self.coefficient).get_surface(), (self.size, self.size))  # type: ignore
        self.element.elm_infos['rect'] = self.element.elm_infos['surface'].get_rect(
        )
        # on repositionne l'élément
        self.element.update()
        super().update()


class DropZone:
    """gestion des zones de déplacements pour les briques"""

    def __init__(self, pos: Vector3 | RelativePos, size: int, interface_nom: str) -> None:
        self.pos = pos
        surface = pygame.Surface(
            (size, size), pygame.SRCALPHA)
        self.element = StaticElement(self, surface, interface_nom)

    def update(self):
        """gestion du relachement du clique"""
        for elm in Brique.briques:
            if (elm != Draggable.dragged and
                self.element.elm_infos['rect'].colliderect(elm.element.elm_infos['rect'])):
                appel('essaie', {'valeur': elm.coefficient})
                return


def initialisation():
    """intialisation"""
    # initilisation des éléments graphiques
    path_geometrique = 'ressources/img/background/fond_geometrique.png'
    path_numerique = 'ressources/img/background/fond_numerique.png'

    DCT_SURFACE['background_geometrique'] = pygame.image.load(
        path_geometrique).convert_alpha()
    
    DCT_SURFACE['background_numerique'] = pygame.image.load(
        path_numerique).convert_alpha()

    lie(lambda: Enigme.create(SequentialEnigme, liste_to_frame), # type: ignore
        'sequence')
    lie(lambda: Enigme.create(BinomialEnigme, liste_to_frame), # type: ignore
        'binomiale')
    lie(lambda: Enigme.create(GeometricEnigme, tableau_to_frame), # type: ignore
        'geometrie')
