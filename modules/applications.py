"""module de gestion des applications"""

from typing import List, Dict, Callable, Any
import pygame
from modules.outils import Texte, Noeud
from modules.graphics import Bouton


# classes


class Shell:
    """gestion du shell virtuel"""

    def __init__(self, texte: Texte, header: str, commandes: Dict[str, Callable[..., None]]) -> None:
        self.texte = texte
        self.header = header
        self.texte.texte = self.header
        self.texte.avance(len(self.header))
        
        self.commandes = commandes
        self.texte.owner = self

    def on_keypress(self, event: pygame.event.Event):
        """réaction clavier"""
        if event.key == pygame.K_RETURN:
            self.execute()

    def execute(self):
        """exécute la ligne de texte comme une commande"""
        # on traite l'avant dernière ligne
        line: str = self.texte.texte.split('\n')[-2]

        # on crée le prochain header
        self.texte.texte += self.header
        self.texte.avance(len(self.header))

        if not line.startswith(self.header):
            return
        raw_line = line[len(self.header):].strip()
        line_split = raw_line.split(' ')

        commande = line_split[0]
        param: List[Any] = line_split[1:] if len(line_split) > 1 else []

        if commande in self.commandes:
            self.commandes[commande](*param)


class Dialogue:
    """classe de gestion des dialogues"""

    def __init__(self, pos: pygame.Vector3, noeud: Noeud, police: pygame.font.Font, interface_nom: str) -> None:
        self.noeud = noeud
        self.choix = 0
        self.texte = Texte(pos, self.noeud.valeur, police, 400, 5, interface_nom)

        self.bouton = Bouton(pos, pygame.Surface(self.texte.element.surface.get_size(), pygame.SRCALPHA), self.next)

    def next(self):
        """passe au dialogue suivant"""
        self.noeud = self.noeud.suivant(self.choix)
        self.texte.texte = self.noeud.valeur
        self.bouton.element.surface = pygame.Surface(self.texte.element.surface.get_size(), pygame.SRCALPHA)
        self.bouton.element.rect = self.bouton.element.surface.get_rect()