"""module de gestion des applications"""

from typing import List, Dict, Callable, Any, TextIO, Set
import json

import pygame

from modules.outils import Noeud, Editeur, lie
from modules.graphics import Bouton, Element, Interface, RelativePos, Texte, Vector3
from modules.enigmes import GeometricCombinaison


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
        if event.button == 1:
            self.state = 1
            self.pos.z += 1
            Interface.current_interface.resort(self.element)
    
    def on_declick(self, event: pygame.event.Event):
        """gestion du relachement du clique"""
        if self.element.elm_infos['rect'].collidepoint(event.pos):
            self.state = 0
            self.pos.z -= 1
            Interface.current_interface.resort(self.element)

    def update(self):
        """méthode de mise à jour"""
        if self.state:
            self.element.pos.x, self.element.pos.y = pygame.mouse.get_pos()


class Brique(Draggable):
    """classe de gestion de brique élémentaire géométrique"""

    briques: Set['Brique'] = set()

    def __init__(self, pos: Vector3, interface_nom: str, composant: List[List[int]] | None = None) -> None:
        super().__init__(pos, pygame.Surface((0, 0)), interface_nom)
        self.interface_nom = interface_nom
        self.coefficient = composant if composant is not None else [[0, 0, 0]]
        self.freeze = False

        Brique.briques.add(self)
        lie(self.reset, 'reset')

    def destroy(self):
        """détruit la brique"""
        self.element.destroy()
        print(self.element.elm_infos['interface'])
        Brique.briques.remove(self)

    def reset(self):
        """réinitialise la brique"""
        for composant in self.coefficient:
            Brique(self.pos + Vector3(0, 50, 0), self.interface_nom, [composant])
        self.destroy()

    def on_keypress(self, event: pygame.event.Event):
        """gestion de touches"""
        if not self.freeze and self.element.elm_infos['rect'].collidepoint(pygame.mouse.get_pos()):
            match event.key:
                case pygame.K_s:
                    self.coefficient[0][0] += 1
                    self.coefficient[0][0] %= 4
                case pygame.K_c:
                    self.coefficient[0][1] += 1
                    self.coefficient[0][1] %= 3
                case pygame.K_r:
                    self.coefficient[0][2] += 1
                    self.coefficient[0][2] %= 4
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
            if elm != self and not elm.state and self.element.elm_infos['rect'].colliderect(elm.element.elm_infos['rect']):
                self.freeze = True
                self.coefficient = elm.coefficient + self.coefficient
                a_detruire.append(elm)
        
        while len(a_detruire):
            a_detruire.pop(0).destroy()
                
    
    def update(self):
        """fonction de mise à jour"""
        self.element.elm_infos['surface'] = GeometricCombinaison(self.coefficient).get_surface() #type: ignore
        self.element.elm_infos['rect'] = self.element.elm_infos['surface'].get_rect()
        # on repositionne l'élément
        self.element.update()
        super().update()


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