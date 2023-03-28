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
    def __init__(self, texte: 'Texte', police: pygame.font.Font, couleur: str, pos: Tuple[float, float]):
        self.pos = pos
        self.texte = texte

        self.police = police
        self.couleur = couleur
        self.nb_line = 20

    def texte_wrapper(self, texte_surfaces: List[pygame.Surface]):
        """retourne le texte à la ligne"""
        height = 21
        return [(surf, (self.pos[0], self.pos[1] + k * height)) for k, surf in enumerate(texte_surfaces)]

    def wrapper(self, surface: pygame.Surface):
        """crée des surfaces de largeur fixe"""
        liste_surface: List[pygame.Surface] = [pygame.Surface((self.texte.max_length, 21))
                                               for _ in range(surface.get_width() //
                                               self.texte.max_length + 1)]

        # la première surface contient le texte le plus ancient
        for k, surf in enumerate(liste_surface):

            if (-((surface.get_width() // self.texte.max_length) * self.texte.max_length)
                    + (self.nb_line) * self.texte.max_length) <= 0:
                surf.blit(surface, (-((surface.get_width() // self.texte.max_length)
                                      * self.texte.max_length)
                                    + (self.nb_line - k - 1) * self.texte.max_length, 0))
            else:
                surf.blit(surface, (-k * self.texte.max_length, 0))
        return liste_surface

    def render_texte(self):
        """affiche le texte"""
        return [self.wrapper(self.police.render(chaine, True, self.couleur)) for chaine in self.texte.texte.split('\n')]

    def render_curseur(self, liste_surfaces: List[Any]):
        """affiche le curseur"""
        surf = pygame.Surface((1, 21))
        surf.fill("#FFFFFF")
        curseur_index = self.texte.texte[:self.texte.curseur].count('\n')
        size = self.police.size(self.texte.texte.split('\n')[curseur_index])
        posy = len(liste_surfaces) - 1
        position = (self.pos[0] + size[0] % (self.texte.max_length), self.pos[1] + posy * size[1])
        return surf, position


class Texte:
    def __init__(self, max_length: int) -> None:
        self.curseur: int = 0
        self.texte: str = ""
        self.max_length = max_length

    def avance_curseur(self):
        """avance le curseur"""
        self.curseur = (self.curseur + 1 if
                        len(self.texte) > self.curseur
                        else self.curseur)

    def recule_curseur(self):
        """avance le curseur"""
        self.curseur = (self.curseur - 1 if
                        self.curseur > 0 else self.curseur)

    def insert_at(self, char: str):
        """insère un caractère"""
        self.texte = self.texte[:self.curseur] + \
            char + self.texte[self.curseur:]
        self.avance_curseur()

    def insert_texte_at(self, texte: str):
        """insère un texte"""
        for char in texte:
            self.insert_at(char)

    def sup_at(self):
        """supprime le caractère à la position du curseur"""
        self.recule_curseur()
        if len(self.texte) > 0:
            self.texte = self.texte[:self.curseur] + \
                self.texte[self.curseur + 1:]

    def vide(self):
        """vide le texte"""
        self.texte = ""

    def truncate(self):
        """on taille le texte à une taille précise"""

        # on vide une partie du texte au bout d'un moment
        if len(self.texte) > 20 * self.max_length:
            taille = len(self.texte) - 20 * self.max_length
            self.texte = self.texte[taille:]

    def newline(self):
        """crée une nouvelle ligne"""
        self.insert_at('\n')


# constante

COMMANDES = [Commande('test', lambda: print('test1')), Commande('scan', lambda: print('test2')),
             Commande('force', lambda: print('test3')), Commande(
                 'check', lambda: print('test4')),
             Commande('connect', lambda: print('test5'))]
