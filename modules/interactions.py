"""module de gestion des applications"""

from typing import List, Dict, Callable
import pygame
from modules.graphics import Element, StaticElement


# classes

class Texte:
    """classe de représentation d'un texte"""

    def __init__(self, pos: pygame.Vector3, texte: str, police: pygame.font.Font,
                 max_width: int, max_lines: int, interface_nom: str | None = None) -> None:
        self.texte = texte
        self.pos = pos
        self.curseur: int = 0
        self.max_width = max_width
        self.max_lines = max_lines
        self.police = police

        surface = pygame.Surface((0, 0))
        self.element = Element(
            self, surface, surface.get_rect(), interface_nom)

    def avance(self):
        """avance le curseur"""
        if self.curseur < len(self.texte):
            self.curseur += 1

    def recule(self):
        """recule le curseur"""
        if self.curseur > 0:
            self.curseur -= 1

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
            self.texte = self.texte[:(self.curseur - 1)] + \
                self.texte[self.curseur:]
            self.recule()
        elif event.key != pygame.K_ESCAPE:
            self.texte = self.texte[:self.curseur] + \
                event.unicode + self.texte[self.curseur:]
            self.avance()

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

        self.element.surface = surface
        self.element.rect = surface.get_rect()


class BackGround:
    """gestion de l'arrière plan"""

    def __init__(self, surface: pygame.Surface, surface_of: pygame.Surface, pos: pygame.Vector3 = pygame.Vector3(0, 0, 0),
                 interface_nom: str | None = None) -> None:
        self.pos = pos
        self.surface_of = surface_of
        self.element = StaticElement(self, surface, interface_nom)

    def update(self):
        """mise à jour"""
        surface = pygame.transform.smoothscale(
            self.element.surface, self.surface_of.get_size())
        self.element.surface = surface
        self.element.rect = surface.get_rect()


class KeyBoardListener:
    """écoute les événements lcaviers"""

    def __init__(self, binds: Dict[int, Callable[[], None]], interface_nom: str) -> None:
        self.pos = pygame.Vector3(0, 0, 0)
        self.binds = binds
        self.element = Element(self, pygame.Surface((0, 0)), pygame.Rect(0, 0, 0, 0 ), interface_nom)

    def on_keypress(self, event: pygame.event.Event):
        """écoute le clavier"""
        if event.key in self.binds:
            self.binds[event.key]()
