"""module de définition des applications"""

from typing import List, Tuple, Any
import pygame

from modules import procesus

# classes

class Application:
    current_app: 'Application'
    window = pygame.Surface((0, 0))

    def __init__(self, icon_nom: str, event_liste: List[int]) -> None:
        self.event_liste = event_liste
        self.icon: pygame.Surface = pygame.image.load(icon_nom)
        self.parent: None | Application = None

    def get_focus(self):
        """focus dans l'application"""
        Application.current_app = self

    def handle_event(self, event: pygame.event.Event) -> None:
        """met à jour correctement le texte selon l'entrée de l'utilisateur"""
        raise NotImplementedError

    def update(self) -> None:
        """mise à jour"""
        raise NotImplementedError


class Link:
    """lien vers une application"""

    def __init__(self, app: Application, icon_nom: str, pos: Tuple[int, int], scale: float = 1) -> None:
        """constructeur"""
        self.icon = pygame.transform.scale_by(
            pygame.image.load(icon_nom), scale)
        self.rect = self.icon.get_rect()
        self.pos = pos
        self.app = app

    def onclick(self):
        """action lors du click"""
        self.app.get_focus()

    def render(self):
        return self.icon, self.pos


class Shell(Application):
    """gestion des shells"""

    def __init__(self, texte_renderer: 'procesus.TextRenderer', interpreter: 'procesus.Interpreter',
                 icon_nom: str, event_liste: List[int]) -> None:
        super().__init__(icon_nom, event_liste)
        self.texte_renderer = texte_renderer
        self.interpreter = interpreter
        self.prefix = "C:/> "

        # initialisation de la ligne de commande
        self.add_prefix()

    def add_prefix(self):
        """ajoute un préfix au début d'une ligne"""
        self.texte_renderer.texte.insert_texte_at(self.prefix)

    def handle_event(self, event: pygame.event.Event):
        """met à jour correctement le texte selon l'entrée de l'utilisateur"""
        if event.type == pygame.KEYDOWN:
            self.event_press(event)

    def event_press(self, event: pygame.event.Event):
        """événements correspondant à KEYDOWN"""
        match event.key:
            case pygame.K_ESCAPE:
                if self.parent is not None:
                    self.parent.get_focus()
            case pygame.K_LEFT:
                self.texte_renderer.texte.recule_curseur()
            case pygame.K_RIGHT:
                self.texte_renderer.texte.avance_curseur()
            case pygame.K_BACKSPACE:
                self.texte_renderer.texte.sup_at()
            case pygame.K_DELETE:
                self.texte_renderer.texte.vide()
            case pygame.K_RETURN:
                self.interpreter.execute(self.texte_renderer.texte.texte.split('\n')[-1])
                self.texte_renderer.texte.newline()
                self.add_prefix()
            case _:
                lettre = event.unicode
                self.texte_renderer.texte.insert_at(lettre)

    def update(self):
        """mise à jour"""
        texte_surfaces = self.texte_renderer.render_texte()
        blit_sequence = self.texte_renderer.texte_wrapper([surf for ls_surf in texte_surfaces for surf in ls_surf])
        Application.window.blits(blit_sequence)
        Application.window.blit(*self.texte_renderer.render_curseur(blit_sequence))


class Game(Application):
    def __init__(self, icon_nom: str, event_liste: List[int]) -> None:
        super().__init__(icon_nom, event_liste)


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYUP:
            self.event_press(event)
    
    def event_press(self, event: pygame.event.Event) -> None:
        """évènements correspondant à KEYUP"""
        match event.key:
            case pygame.K_ESCAPE:
                if self.parent is not None:
                    self.parent.get_focus()
            case _:
                ...

    def update(self):
        """mise à jour"""
        pass


class Desktop(Application):
    """gestion des bureaux"""

    def __init__(self, background_nom: str, icon_nom: str, links: List[Link], event_liste: List[int]) -> None:
        super().__init__(icon_nom, event_liste)
        self.background = pygame.transform.scale(
            pygame.image.load(background_nom), Application.window.get_size())

        self.links = links
        for link in links:
            link.app.parent = self

    def handle_event(self, event: pygame.event.Event) -> None:
        """gère les événements"""
        for link in self.links:
            pos = (event.pos[0] - link.pos[0], event.pos[1] - link.pos[1])
            if link.rect.collidepoint(pos):
                link.onclick()

    def update(self) -> None:
        """met à jour"""
        Application.window.blit(self.background, (0, 0))
        Application.window.blits([link.render() for link in self.links])