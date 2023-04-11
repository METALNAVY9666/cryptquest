"""module de prototypage"""
from typing import List
import pygame
from modules.graphics import POLICE, Interface, Bouton
from modules.interactions import Texte, BackGround, KeyBoardListener

WINDOW = pygame.display.set_mode((1080, 720))


# fonctions

def initialisation():
    Interface.current_interface = Interface('bureau')
    Interface('shell')

    # image de fond
    surface = pygame.image.load('ressources/img/background/desktop.jpg')
    BackGround(surface, WINDOW, interface_nom='bureau')
    BackGround(pygame.Surface((10, 10)), WINDOW, interface_nom='shell')

    # shell
    surface_shell_icon = pygame.image.load('ressources/img/icons/cmd.png')
    surface_shell_icon = pygame.transform.smoothscale_by(surface_shell_icon, 0.4)
    KeyBoardListener({pygame.K_ESCAPE: lambda: Interface.change_interface('bureau')}, 'shell')
    Bouton(pygame.Vector3(100, 100, 1), surface_shell_icon,
           lambda: Interface.change_interface('shell'), interface_nom='bureau')
    Texte(pygame.Vector3(100, 50, 1), '', POLICE, 600, 20, 'shell')


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