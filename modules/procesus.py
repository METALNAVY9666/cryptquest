"""module de gestion des classes de traitement des données"""

from typing import Callable, Any, Tuple, List, Dict
import pygame


class Commande:

    commandes_nom_dct: Dict[str, 'Commande'] = {}

    def __init__(self, nom: str, run: Callable[[], Any]) -> None:
        self.nom = nom
        self.run = run
        Commande.commandes_nom_dct[nom] = self

    @classmethod
    def found_by_name(cls, nom: str):
        """renvoie la commande correspondant au nom"""
        return Commande.commandes_nom_dct[nom]

class Interpreter:
    def __init__(self, texte: 'Texte') -> None:
        self.texte = texte

    def execute(self, commande: str):
        """exécute une commande donnée"""
        # cas de commande vide
        if commande == "":
            return
        
        # on commence par passer à la ligne suivante
        self.texte.newline()

        # on traite ensuite les différentes commandes
        commande = commande.strip()
        tokens = commande.split(" ")
        if tokens[0] in Commande.commandes_nom_dct:
            Commande.found_by_name(tokens[0]).run()
        else:
            self.texte.insert_texte_at('Commande non reconnue')

        # saut de ligne de fin d'exécution
        self.texte.newline()


class TextRenderer:
    def __init__(self, texte: 'Texte', pos: Tuple[float, float]):
        self.pos = pos
        self.texte = texte

    def texte_wrapper(self, texte_surfaces: List[pygame.Surface]):
        """retourne le texte à la ligne"""
        height = texte_surfaces[0].get_height()
        return ((surf, (self.pos[0], self.pos[1] + k * height)) for k, surf in enumerate(texte_surfaces))

    def split_surface(self, surface: pygame.Surface):
        """découpe une longue surface selon le paramètre max_length"""
        liste_surface: List[pygame.Surface] = [pygame.Surface((self.texte.max_length, surface.get_height()))
                                               for _ in range(surface.get_width() // self.texte.max_length + 1)]

        for k, surf in enumerate(liste_surface):
            surf.blit(surface, (-k * self.texte.max_length, 0))
        return liste_surface

    def render_texte(self, texte: str, max_length: int):
        """affiche le texte"""
        return self.split_surface(self.texte.police.render(str(self.texte), True, "#30FF00"))

    def render_curseur(self, texte_surfaces: List[pygame.Surface]):
        """affiche le curseur"""
        surf = pygame.Surface((1, texte_surfaces[0].get_height()))
        surf.fill("#FFFFFF")
        size = self.texte.police.size(
            str(self.texte)[:self.texte.curseur + len(self.texte.pre_texte)])
        position = (self.pos[0] + size[0] % (self.texte.max_length), self.pos[1] +
                    (size[0] // (self.texte.max_length)) * size[1])
        return surf, position


class Texte:
    def __init__(self, max_length: int, police: pygame.font.Font) -> None:
        self.curseur: int = 0
        self.texte: List[str] = []
        self.pre_texte: List[str] = []
        self.max_length = max_length
        self.police = police

    def avance_curseur(self):
        """avance le curseur"""
        self.curseur = (self.curseur + 1 if
                        len(self.texte) + len(self.pre_texte) > self.curseur
                        else self.curseur)

    def recule_curseur(self):
        """avance le curseur"""
        self.curseur = (self.curseur - 1 if
                        self.curseur > len(self.pre_texte) else self.curseur)

    def insert_at(self, char: str):
        """insère un caractère"""
        self.texte.insert(self.curseur, char)
        self.avance_curseur()

    def insert_texte_at(self, texte: str):
        """insère un texte"""
        for char in texte:
            self.insert_at(char)

    def sup_at(self):
        """supprime le caractère à la position du curseur"""
        self.recule_curseur()
        if len(self.texte) > 0:
            self.texte.pop(self.curseur - len(self.pre_texte))

    def vide(self):
        """vide le texte"""
        self.texte.clear()

    def register(self):
        """enregistre le texte courant dans pre_texte"""
        self.pre_texte += self.texte
        self.vide()

    def newline(self):
        """crée une nouvelle ligne"""
        size = self.police.size(str(self)[:self.curseur + len(self.pre_texte)])
        init_pos_y: int = (size[0] // (self.max_length))
        pos_y = init_pos_y
        while pos_y - init_pos_y == 0:
            self.insert_at(" ")
            size = self.police.size(str(self)[:self.curseur + len(self.pre_texte)])
            pos_y: int = (size[0] // (self.max_length))

    def __str__(self) -> str:
        return "".join(self.pre_texte + self.texte)

    def get_texte(self) -> str:
        return "".join(self.texte)


# constante

COMMANDES = [Commande('test', lambda: print('test1')), Commande('scan', lambda: print('test2')),
             Commande('force', lambda: print('test3')), Commande('check', lambda: print('test4')),
             Commande('connect', lambda: print('test5'))]


