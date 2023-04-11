"""module de gestion des applications"""

from typing import List, Dict, Callable, Any
import pygame
<<<<<<< Updated upstream
from modules.outils import Texte
=======
from modules.graphics import Element, StaticElement
from modules.outils import CrypteurPair
>>>>>>> Stashed changes


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


class Password:
    """gestion de la partie mdp avant le jeu"""

    def __init__(self) -> None:
        with open('ressources/files/file.txt') as file:
            # self.mdp = CrypteurPair.decode_AES(file.readlines()[0])
            self.mdp = file.readlines()[0]

    def update(self):
        ...