"""module de gestion des applications"""

from typing import List, Dict, Callable, Any, TextIO
import json

import pygame

from modules.outils import Noeud, Editeur
from modules.graphics import Bouton, Element, RelativePos, Texte, Vector3


# classes


class Shell:
    """gestion du shell virtuel"""

    def __init__(self, texte: Editeur, header: str, commandes: Dict[str, Callable[..., None]]) -> None:
        self.texte = texte
        self.header = header
        self.texte.texte = self.header
        self.texte.avance(len(self.header))
        self.texte.protected_curseur_pos = self.texte.curseur

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
        self.texte.protected_curseur_pos = self.texte.curseur

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

    def __init__(self, pos: Vector3 | RelativePos, noeud: Noeud, police: pygame.font.Font, interface_nom: str) -> None:
        self.noeud = noeud
        self.texte = Texte(pos, police, '#FFFFFF',
                           self.noeud.valeur, interface_nom)

        self.bouton = Bouton(pos, pygame.Surface(self.texte.element.elm_infos["surface"].get_size(), pygame.SRCALPHA),
                             self.next, interface_nom=interface_nom)

    def next(self):
        """passe au dialogue suivant"""
        temp: Noeud | None = self.noeud.suivant()

        if temp is None:
            return

        self.noeud = temp
        self.texte.texte = self.noeud.valeur

        self.bouton.element.elm_infos["surface"] = pygame.Surface(
        self.texte.element.elm_infos["surface"].get_size(), pygame.SRCALPHA)
        self.bouton.element.elm_infos["rect"] = self.bouton.element.elm_infos["surface"].get_rect()


class Draggable:
    """objet qu'on peut bouger"""

    def __init__(self, pos: Vector3, surface: pygame.Surface, interface_nom: str) -> None:
        self.pos = pos
        self.state = 0
        self.element = Element(self, surface, surface.get_rect(), interface_nom)

    def on_click(self, event: pygame.event.Event):
        """gestion du clique"""
        if event.button == 1 and self.element.elm_infos['rect'].collidepoint(event.pos):
            self.state = 1
    
    def on_declick(self, event: pygame.event.Event):
        """gestion du relachement du clique"""
        self.state = 0

    def update(self):
        """méthode de mise à jour"""
        if self.state:
            self.element.pos.x, self.element.pos.y = pygame.mouse.get_pos()


class Brique(Draggable):
    """classe de gestion de brique élémentaire géométrique"""

    def __init__(self, pos: Vector3, surface: pygame.Surface, interface_nom: str) -> None:
        super().__init__(pos, surface, interface_nom)


# fonctions

def load_dialogue(dialogue_file: TextIO):
    """charge les noeuds de dialogues"""
    dialogue_dct: Dict[str, Dict[str, Any]] = json.load(dialogue_file)

    # créations des noeuds

    for nom, valeur in dialogue_dct["noeuds"].items():
        Noeud(valeur, nom)

    # relations entre les noeuds

    for nom, relations in dialogue_dct['relations'].items():
        noeud = Noeud.get_by_nom(nom)

        prerequis: List[str] = relations["prerequis"] if "prerequis" in relations else []
        in_prerequis: List[str] = relations["prerequis entrant"] if "prerequis entrant" in relations else []
        triggers: List[str] = relations["triggers"] if "triggers" in relations else []
        end: List[str] = relations['end'] if "end" in relations else []
        typ: str = relations['type'] if "end" in relations else "exact"

        noeud.set_enfant(end)
        noeud.set_mode(typ, in_prerequis, prerequis, triggers)