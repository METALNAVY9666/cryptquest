"""module de gestion des applications"""

import json
import random
from typing import Any, Callable, Dict, List, TextIO, Tuple

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
        self.texte.curseur['private'] = self.texte.curseur['public']

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
                    self.texte.ajoute_texte("   lis le help stp")
                else:
                    self.texte.ajoute_texte("   paramètres erronés\n")

        # on crée le prochain header
        self.texte.texte += self.header
        self.texte.avance(len(self.texte.texte) - len(backup_texte))
        self.texte.curseur['private'] = self.texte.curseur['public']


class Dialogue:
    """classe de gestion des dialogues"""

    # ajout d'une surface de fond
    def __init__(self, pos: Vector3 | RelativePos, noeud: Noeud,
                 surf_info: Tuple[pygame.Surface, pygame.font.Font], interface_nom: str) -> None:
        self.noeud = noeud
        self.texte = Texte(pos, police=surf_info[1], surface=surf_info[0], couleur='#FFFFFF',
                           texte=self.noeud.valeur, interface_nom=interface_nom)
        self.bouton = self.init_button(pos, interface_nom)

    def init_button(self, pos: Vector3 | RelativePos, interface_nom: str) -> Bouton:
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

        self.state = False

        # visualisation de l'argent
        self.element = Texte(pos, police=pygame.font.SysFont('Arial', 35, True), couleur='#c521de',
                             texte='0€', interface_nom=interface_nom)

    def scan(self):
        """simule un scan du réseau"""
        if self.state:
            self.texte.ajoute_texte('  Machine infectée, accès réseau coupé\n')
            return

        self.machines.clear()
        nb_machines = random.randint(0, 5)
        for _ in range(nb_machines):
            lst: List[str] = []
            for _ in range(4):
                lst.append(str(random.randint(0, 255)))

            self.machines.append(".".join(lst))

        if nb_machines == 0:
            self.texte.ajoute_texte('  Aucune machine sur le réseau\n')

        for machine in self.machines:
            self.texte.ajoute_texte(f'  machine: {machine}\n')

    def hack(self, add_ip: str):
        """simule une infection"""
        if add_ip not in self.machines:
            self.texte.ajoute_texte('machine inconnue\n')
            return

        chance = random.random()
        if chance > 0.9:
            self.texte.ajoute_texte(
                'infection réussite, vole des données réussi\n')
            self.element.texte = f"{int(self.element.texte[:-1]) + random.randint(10, 200)}€"
        elif 0.9 < chance:
            self.texte.ajoute_texte('infection ratée\n')
        else:
            self.texte.ajoute_texte(
                'infection désastreuse, votre machine est contaminée\n')
            self.texte.ajoute_texte(
                "Rendez-vous sur l'application de sécurité\n")
            if not self.state:
                appel('lancement', {})
                self.state = 1


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
        in_triggers: List[str] = relations["triggers"] if "triggers" in relations else [
        ]
        out_triggers: List[str] = (relations["triggers sortants"]
                                   if "triggers sortants" in relations else [])
        end: List[str] = relations['end'] if "end" in relations else []
        typ: str = relations['type'] if "end" in relations else "exact"

        noeud.set_enfant(end)
        noeud.set_mode(typ, in_prerequis, prerequis,
                       (in_triggers, out_triggers))


def aide(texte: Editeur):
    """écrit l'aide dans le shell"""
    texte.ajoute_texte('Les commandes disponibles sont :\n')
    texte.ajoute_texte(
        "    hack -ip <= tente de voler les données d'une machine\n")
    texte.ajoute_texte("    help <= affiche l'aide\n")
    texte.ajoute_texte("    reset <= réinitialise les formes géométriques\n")
    texte.ajoute_texte('    scan <= scan le réseau\n')
    texte.ajoute_texte("    tutoriel <= lance le tutoriel\n")


def tutoriel(editeur: Editeur):
    """joue le tutoriel"""
    texte = ("cliquez sur les textes de dialogues pour passer au suivant\n" +
             "le but est de résoudre les énigmes pour sauver l'ordinateur\n" +
             "Pour les énigmes de type géométrique, si vous avez un doute, laissez un carré\n" +
             "Pour les énigmes de type chemin, le but est " +
             "de passer par toutes les valeurs indiquées\n" +
             "en alternant lignes et colonnes, en commençant par une colonne")

    for ligne in texte.split('\n'):
        editeur.ajoute_texte('  ' + ligne + '\n')
