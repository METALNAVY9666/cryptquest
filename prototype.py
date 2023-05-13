"""module de prototypage"""

from typing import List
import pygame
from modules.graphics import POLICE, Interface, Bouton, RelativePos
from modules.applications import Shell, Dialogue, load_dialogue
from modules.outils import (BackGround, KeyBoardListener, Noeud, Editeur,
                            lie, appel)

from modules.enigmes import SequentialEnigme, BinomialEnigme, NumericEnigme

WINDOW = pygame.display.set_mode((1080, 720))
RelativePos.default_window = WINDOW


# fonctions

def initialisation_bureaux():
    """initialisation du bureaux"""
    Interface.current_interface = Interface('bureau')

    # image de fond
    surface = pygame.image.load('ressources/img/background/desktop.jpg')
    BackGround(surface, WINDOW, interface_nom='bureau')

    # shell icon
    surface_shell_icon = pygame.image.load('ressources/img/icons/cmd.png')
    surface_shell_icon = pygame.transform.smoothscale_by(
        surface_shell_icon, 0.4)

    Bouton(pygame.Vector3(100, 100, 1), surface_shell_icon,
           lambda: Interface.change_interface('shell'), interface_nom='bureau')


def initialisation_shell():
    """initialisation du shell"""
    Interface('shell')

    BackGround(pygame.Surface((10, 10)), WINDOW, interface_nom='shell')

    texte = Editeur(pygame.Vector3(100, 50, 1), '', POLICE, 600, 20, 'shell')
    Shell(texte, r"C:\Users> ", {'ls': lambda: appel('test', {})})

    KeyBoardListener(
        {pygame.K_ESCAPE: lambda: Interface.change_interface('bureau')}, 'shell')


def initialisation_jeux():
    """initialisation du coeur principale"""
    Interface('game')

    KeyBoardListener(
        {pygame.K_ESCAPE: lambda: Interface.change_interface('bureau')}, 'game')

    surface_game_icon = pygame.image.load('ressources/img/icons/game.png')
    surface_game_icon = pygame.transform.smoothscale_by(surface_game_icon, 0.4)
    Bouton(pygame.Vector3(300, 100, 1), surface_game_icon,
           lambda: Interface.change_interface('game'))
    
    lie(lambda: NumericEnigme.create(SequentialEnigme), 'sequence') # type: ignore
    lie(lambda: NumericEnigme.create(BinomialEnigme), 'binomiale') # type: ignore


def initialisation():
    # initialisation du mot de passe
    with open('ressources/files/file.txt') as file:
        # self.mdp = CrypteurPair.decode_AES(file.readlines()[0])
        mdp = file.readlines()[0]

    # bureaux
    initialisation_bureaux()

    # shell
    initialisation_shell()

    # jeu
    initialisation_jeux()

    # dialogues
    with open('ressources/data/dialogue.json', 'r', encoding="utf-8") as fichier:
        load_dialogue(fichier)

    lie(lambda **_: print('ok'), "test2")

    Dialogue(RelativePos(0.5, 0, 1, aligne='top'),
             Noeud.get_by_nom('A'), POLICE, 'game')


def handle_event(events: List[pygame.event.Event]):
    """gestion des événements"""
    for event in events:
        match event.type:
            case pygame.QUIT:
                return False
            case pygame.KEYDOWN:
                Interface.current_interface.on_keypress(event)
            case pygame.MOUSEBUTTONDOWN:
                Interface.current_interface.on_click(event)
            case _:
                ...
    return True


def update():
    WINDOW.fill('#000000')
    Interface.current_interface.update()
    WINDOW.blits(Interface.current_interface.render())


# initialisation

initialisation()

# boucle principale

running = True

while running:
    running = handle_event(pygame.event.get())
    update()
    pygame.display.flip()
