"""module outils"""
from typing import Any, Callable, Dict, List
import random

import pygame

from modules.graphics import Element, StaticElement, Vector3

# système observeur

evenement: Dict[str, List[Callable[..., Any]]] = {}


def lie(fnct: Callable[..., Any], nom: str):
    """lie une fonction à un événement"""
    if nom in evenement:
        evenement[nom].append(fnct)
    else:
        evenement[nom] = [fnct]


def delie(fnct: Callable[..., Any], nom: str):
    """délie une fonction d'un événement"""
    if nom in evenement and fnct in evenement[nom]:
        evenement[nom].remove(fnct)


def vide(nom: str):
    """detruit un événement"""
    if nom in evenement:
        del evenement[nom]


def appel(nom: str, data: Dict[str, Any]):
    """appelle les fonctions associées"""

    if not nom in evenement:
        return
    
    appel_stack = evenement[nom][:]
    
    for fnct in appel_stack:
        fnct(**data)


def set_dct(valeur: Any, clef: str, dct: Dict[str, Any]):
    """change la valeur de la clef"""
    if clef in dct:
        dct[clef] = valeur


# classe

class Editeur:
    """classe de représentation d'un texte"""

    def __init__(self, pos: Vector3, texte: str, police: pygame.font.Font,
                 max_width: int, max_lines: int, interface_nom: str | None = None) -> None:
        self.owner: Any | None = None

        self.texte = texte
        self.pos = pos
        self.curseur: int = 0
        self.protected_curseur_pos: int = 0
        self.max_width = max_width
        self.max_lines = max_lines
        self.police = police

        surface = pygame.Surface((0, 0))
        self.element = Element(
            self, surface, surface.get_rect(), interface_nom)

    def avance(self, k: int = 1):
        """avance le curseur"""
        if self.curseur + k <= len(self.texte):
            self.curseur += k

    def recule(self, k: int = 1):
        """recule le curseur"""
        if self.curseur - k >= 0:
            self.curseur -= k

    def on_keypress(self, event: pygame.event.Event):
        """réagit aux événements claviers"""
        if event.key == pygame.K_LEFT:
            self.recule()
        elif event.key == pygame.K_RIGHT:
            self.avance()

        elif event.key == pygame.K_RETURN:
            self.texte = self.texte[:self.curseur] + \
                '\n' + self.texte[self.curseur:]
            self.avance()

        elif event.key == pygame.K_BACKSPACE:
            if self.curseur > self.protected_curseur_pos:
                self.texte = self.texte[:(self.curseur - 1)] + \
                    self.texte[self.curseur:]
                self.recule()

        elif event.key != pygame.K_ESCAPE:
            self.texte = self.texte[:self.curseur] + \
                event.unicode + self.texte[self.curseur:]
            self.avance()

        if self.owner is not None and hasattr(self.owner, 'on_keypress'):
            self.owner.on_keypress(event)

    def ajoute_texte(self, texte: str):
        """ajoute du texte"""
        self.texte += texte

    def update(self):
        """mise à jour de l'objet"""
        textes = self.texte.split('\n')
        width_surfaces = [[elm[4]
                           for elm in self.police.metrics(texte)] for texte in textes]

        char_ind_start = 0
        textures: List[pygame.Surface] = []
        height = self.police.size(self.texte)[1]
        curseur_surface = pygame.Surface((2, height))
        curseur_surface.fill('#FFFFFF')

        curseur_pos = [0, 0]

        curseur_compteur = 0
        lines_sup = 0

        # on itère pour toutes les lignes
        for line, width_surface in enumerate(width_surfaces):
            somme = 0
            # on itère pour chaque caractère de la ligne
            for rang, width in enumerate(width_surface):
                somme += width
                curseur_compteur += 1
                # si la longueur de la ligne dépasse la longueur maximale
                # on passe à la ligne suivante
                if somme > self.max_width:
                    textures.append(self.police.render(
                        textes[line][char_ind_start:rang], True, '#4AF626'))
                    char_ind_start = rang
                    somme = width
                    lines_sup += 1

                # si on a atteint la position du curseur
                # on sauvegarde sa position
                if curseur_compteur == self.curseur:
                    curseur_pos = [somme, (line + lines_sup) * height]

            textures.append(self.police.render(
                textes[line][char_ind_start:], True, '#4AF626'))
            char_ind_start = 0
            curseur_compteur += 1
            if curseur_compteur == self.curseur:
                curseur_pos = [0, (line + lines_sup + 1) * height]

        surface = pygame.Surface((max(texture.get_width() for texture in textures) + 2,
                                  self.max_lines * height))

        # devient vrai lorque le texte a atteint la fin de la zone
        do_move = len(textures) > self.max_lines
        for line, texture in enumerate(textures):
            if do_move:
                surface.blit(
                    texture, (0, height * (self.max_lines - len(textures) + line)))
            else:
                surface.blit(texture, (0, height * line))

        # on place correctement le curseur
        offset = (len(textures) - self.max_lines) * height
        if do_move and curseur_pos[1] >= offset:
            curseur_pos[1] -= offset
            surface.blit(curseur_surface, curseur_pos)
        elif do_move:
            surface.blit(curseur_surface, (0, 0))
        else:
            surface.blit(curseur_surface, curseur_pos)

        self.element.elm_infos["surface"] = surface
        self.element.elm_infos["rect"] = surface.get_rect()


class BackGround:
    """gestion de l'arrière plan"""

    def __init__(self, surface: pygame.Surface, surface_of: pygame.Surface, pos: Vector3 = Vector3(0, 0, 0),
                 interface_nom: str | None = None) -> None:
        self.pos = pos
        self.surface_of = surface_of
        self.element = StaticElement(self, surface, interface_nom)

    def update(self):
        """mise à jour"""
        surface = pygame.transform.smoothscale(
            self.element.elm_infos["surface"], self.surface_of.get_size())
        self.element.elm_infos["surface"] = surface
        self.element.elm_infos["rect"] = surface.get_rect()


class KeyBoardListener:
    """écoute les événements claviers"""

    def __init__(self, binds: Dict[int, Callable[[], None]], interface_nom: str) -> None:
        self.pos = Vector3(0, 0, 0)
        self.binds = binds
        self.element = Element(self, pygame.Surface(
            (0, 0)), pygame.Rect(0, 0, 0, 0), interface_nom)

    def on_keypress(self, event: pygame.event.Event):
        """écoute le clavier"""
        if event.key in self.binds:
            self.binds[event.key]()


class Noeud:
    """représentation d'un noeud d'un graphe orienté"""
    noeuds: Dict[str, 'Noeud'] = {}

    def __init__(self, valeur: Any, nom: str) -> None:
        self.valeur = valeur
        self.children: List['Noeud'] = []
        self.nom = nom
        self.mode = 'exact'

        self.prerequis: Dict[str, bool] = {}
        self.in_prerequis: Dict[str, bool] = {}
        self.triggers: List[str] = []

        Noeud.noeuds[nom] = self

    def set_enfant(self, enfants: List['str']):
        """enfants du noeud"""
        self.children = [Noeud.get_by_nom(enfant) for enfant in enfants]

    def set_mode(self, mode: str, in_prerequis: List[str], prerequis: List[str], triggers: List[str]):
        """change le mode de sélection du noeud suivant"""
        self.mode = mode

        for nom in prerequis:
            self.prerequis[nom] = False
            lie(lambda **_: set_dct(True, nom, self.prerequis), nom)

        for nom in in_prerequis:
            self.prerequis[nom] = False
            lie(lambda **_: set_dct(True, nom, self.in_prerequis), nom)

        # les triggers déclenche les événements de type None -> None
        for nom in triggers:
            self.triggers.append(nom)
    
    def arrive(self):
        """exécuter lors de l'arrivée sur ce noeud"""
        # cas particulier lié au jeu
        if any(val in self.triggers for val in ('binomiale', 'geometrique', 'sequence', 'chemin')):
            self.prerequis['enigme_resolu'] = False
            lie(lambda **_: set_dct(True, 'enigme_resolu', self.prerequis), 'enigme_resolu')

        # on active les triggers du noeud enfant
        for nom in self.triggers:
            appel(nom, {})
    
    def quitte(self):
        """exécuter lors du départ du noeud"""
        # cas particulier lié au jeu
        if 'enigme_resolu' in self.prerequis:
            vide('enigme_resolu')

    def suivant(self):
        """passe au noeud suivant"""
        if not all(self.prerequis.values()) or len([enfant for enfant in self.children 
                                                    if all(enfant.in_prerequis)]) == 0:
            return None

        noeud = self.children[0]

        match self.mode:
            case 'exact':
                if len(self.children) > 1:
                    # trop d'enfant, trop de choix
                    raise ValueError
                
                if not all(noeud.in_prerequis.values()):
                    return None

            case 'random':
                noeud = random.choice([enfant for enfant in self.children if
                                       all(enfant.in_prerequis.values())])

            case _:
                # clef incorrect
                raise KeyError
        self.quitte()
        noeud.arrive()

        return noeud

    @classmethod
    def get_by_nom(cls, nom: str):
        """renvoie le noeud correspondant au nom"""
        # erreur intentionnelle
        return cls.noeuds[nom]
