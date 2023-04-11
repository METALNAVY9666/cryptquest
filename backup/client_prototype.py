import pygame

from modules.applications import Desktop, Shell, Link, Application, Game
from modules.procesus import Texte, TextRenderer, Interpreter

pygame.init()

# constantes

WINDOW = pygame.display.set_mode((1080, 640), pygame.RESIZABLE)
POLICE = pygame.font.Font(
    'ressources/fonts/sourcecodepro.ttf', 16)  # font à changer
POLICE.bold = True

# fonctions de base


def clear():
    """nettoie l'écran"""
    WINDOW.fill("#000000")


def initialise():
    """initialisation"""
    Application.window = WINDOW

    # variables

    text = Texte(600)
    texte_renderer = TextRenderer(text, POLICE, '#30FF50', (100, 100))
    interpreter = Interpreter(text)
    shell = Shell(texte_renderer, interpreter,
                'ressources/img/icons/cmd.png', [pygame.KEYDOWN])
    game = Game('ressources/img/icons/game.png', [pygame.KEYUP])
    bureaux = Desktop('ressources/img/background/desktop.jpg', 'ressources/img/icons/bureaux.png',
                    [Link(shell, 'ressources/img/icons/cmd.png',
                            (100, 100), 0.35),
                    Link(game, 'ressources/img/icons/game.png',
                            (250, 100), 0.17)], [pygame.MOUSEBUTTONDOWN])
    
    Application.current_app = shell
    bureaux.get_focus()


# boucle principale
def main():
    """boucle principale"""
    running = True

    while running:
        clear()

        events = pygame.event.get()
        for evnt in events:
            match evnt.type:
                case pygame.QUIT:
                    running = False
                case _:
                    ...
            # on passe l'événement dans l'application
            if evnt.type in Application.current_app.event_liste:
                Application.current_app.handle_event(evnt)

        Application.current_app.update()

        pygame.display.flip()

# appel de la fonction principale

initialise()
main()
