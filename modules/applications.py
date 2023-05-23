"""module de gestion des applications"""

import json
import random
from typing import Any, Callable, Dict, List, TextIO

import pygame

from modules.graphics import Bouton, RelativePos, Texte, Vector3
from modules.outils import Editeur, Noeud, appel

# classes


class Shell:
    """gestion du shell virtuel"""

    def __init__(self, texte: Editeur, header: str,
        commandes: Dict[str, Callable[..., Any]]) -> None:
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
        backup_texte = self.texte.texte

        # on traite l'avant dernière ligne
        line: str = self.texte.texte.split('\n')[-2]

        if not line.startswith(self.header):
            return
        raw_line = line[len(self.header):].strip()
        line_split = raw_line.split(' ')

        commande = line_split[0]
        param: List[Any] = line_split[1:] if len(line_split) > 1 else []

        if commande in self.commandes:
            try:
                self.commandes[commande](*param)
            except TypeError:
                if random.randint(0, 9) == 7:
                    self.texte.ajoute_texte("   lis la doc stp")
                else:
                    self.texte.ajoute_texte("   paramètres érronés\n")

        # on crée le prochain header
        self.texte.texte += self.header
        self.texte.avance(len(self.texte.texte) - len(backup_texte))
        self.texte.protected_curseur_pos = self.texte.curseur


class Dialogue:
    """classe de gestion des dialogues"""

    # ajout d'une surface de fond
    def __init__(self, pos: Vector3 | RelativePos, noeud: Noeud,
                 police: pygame.font.Font, interface_nom: str) -> None:
        self.noeud = noeud
        self.texte = Texte(pos, police=police, couleur='#FFFFFF',
                           texte=self.noeud.valeur, interface_nom=interface_nom)

        self.bouton = self.init_button(pos, interface_nom)

    def init_button(self, pos, interface_nom):
        """initialise le bouton"""
        size = self.texte.element.elm_infos["surface"].get_size()
        surface = pygame.Surface(size, pygame.SRCALPHA)
        return Bouton(pos, surface, fonction=self.next, interface_nom=interface_nom)

    def next(self):
        """passe au dialogue suivant"""
        temp: Noeud | None = self.noeud.suivant()

        if temp is None:
            return

        self.noeud = temp
        self.texte.texte = self.noeud.valeur

        self.bouton.element.elm_infos["surface"] = pygame.Surface(
            self.texte.element.elm_infos["surface"].get_size(), pygame.SRCALPHA)
        self.bouton.element.elm_infos["rect"] = self.bouton.element.elm_infos["surface"].get_rect(
        )


class Reseau:
    """simule faiblement un réseau"""

    def __init__(self, texte: Editeur, pos: Vector3 | RelativePos, interface_nom: str) -> None:
        self.machines: List[str] = []
        self.texte = texte

        # visualisation de l'argent
        self.element = Texte(pos, police=pygame.font.SysFont('Arial', 35, True), couleur='#c521de',
                             texte='0€', interface_nom=interface_nom)

    def scan(self):
        """simule un scan du réseau"""
        self.machines.clear()
        nb_machines = random.randint(0, 5)
        for _ in range(nb_machines):
            lst: List[str] = []
            for _ in range(4):
                lst.append(str(random.randint(0, 255)))

            self.machines.append(".".join(lst))

        for machine in self.machines:
            self.texte.ajoute_texte(f'  machine: {machine}\n')

    def hack(self, add_ip: str):
        """simule une infection"""
        if not add_ip in self.machines:
            self.texte.ajoute_texte('machine inconnue\n')
            return

        chance = random.random()
        if chance > 0.6:
            self.texte.ajoute_texte(
                'infection réussite, vole des données réussi\n')
            self.element.texte = f"{int(self.element.texte[:-1]) + random.randint(10, 200)}€"
        elif 0.4 < chance:
            self.texte.ajoute_texte('infection ratée\n')
        else:
            self.texte.ajoute_texte(
                'infection désastreuse, votre machine est contaminée\n')
            appel('lancement', {})


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

        prerequis: List[str] = relations["prerequis"] if "prerequis" in relations else [
        ]
        in_prerequis: List[str] = (relations["prerequis entrant"]
            if "prerequis entrant" in relations else [])
        triggers: List[str] = relations["triggers"] if "triggers" in relations else []
        end: List[str] = relations['end'] if "end" in relations else []
        typ: str = relations['type'] if "end" in relations else "exact"

        noeud.set_enfant(end)
        noeud.set_mode(typ, in_prerequis, prerequis, triggers)


def aide(texte: Editeur):
    """écrit l'aide dans le shell"""
    texte.ajoute_texte('Les commandes disponibles sont :\n')
    texte.ajoute_texte(
        "    hack -ip <= tente de voler les données d'une machine\n")
    texte.ajoute_texte("    help <= affiche l'aide\n")
    texte.ajoute_texte("    ls <= complète un événement\n")
    texte.ajoute_texte('    scan <= scan le réseau\n')
    texte.ajoute_texte("    tutoriel <= lance le tutoriel\n")
