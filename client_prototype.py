import pygame
from typing import List, Tuple, Any

pygame.init()

# constantes

WINDOW = pygame.display.set_mode((1080, 640), pygame.RESIZABLE)
POLICE = pygame.font.Font(
    'ressources/fonts/sourcecodepro.ttf', 16)  # font à changer
POLICE.bold = True

# classes de gameplay


class Application:
    current_app: 'Application'

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
    def __init__(self, app: Application, icon_nom: str, pos: Tuple[int, int], scale: float=1) -> None:
        """constructeur"""
        self.icon = pygame.transform.scale_by(pygame.image.load(icon_nom), scale)
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
    def __init__(self, icon_nom: str, event_liste: List[int]) -> None:
        super().__init__(icon_nom, event_liste)

    def handle_event(self, event: pygame.event.Event):
        """met à jour correctement le texte selon l'entrée de l'utilisateur"""
        if event.type == pygame.KEYDOWN:
            self.event_press(event)

    def event_press(self, event: pygame.event.Event):
        """événments correspondant à KYEDOWN"""
        match event.key:
            case pygame.K_ESCAPE:
                if self.parent is not None:
                    self.parent.get_focus()
            case pygame.K_LEFT:
                texte.recule_curseur()
            case pygame.K_RIGHT:
                texte.avance_curseur()
            case pygame.K_BACKSPACE:
                texte.sup_at()
            case pygame.K_RETURN:
                texte.newline()
            case _:
                lettre = event.unicode
                texte.insert_at(lettre)

    def update_key(self):
        keys = pygame.key.get_pressed()
        for key in keys:
            match key:
                case

    def update(self):
        """mise à jour"""
        self.update_key()
        texte_surfaces = render_texte(str(texte), 100)
        blit_sequence: Any = texte_wrapper(texte_surfaces, (100, 100))
        WINDOW.blits(blit_sequence)
        WINDOW.blit(*render_curseur(texte_surfaces, (100, 100), 100))


class Desktop(Application):
    """gestion des bureaux"""
    def __init__(self, background_nom: str, icon_nom: str, links: List[Link], event_liste: List[int]) -> None:
        super().__init__(icon_nom, event_liste)
        self.background = pygame.transform.scale(pygame.image.load(background_nom), WINDOW.get_size())

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
        WINDOW.blit(self.background, (0, 0))
        WINDOW.blits([link.render() for link in self.links])


# fonctions et classes de maniment du texte


class Texte:
    def __init__(self, max_length: int) -> None:
        self.curseur: int = 0
        self.texte: List[str] = []
        self.max_length = max_length

    def avance_curseur(self):
        """avance le curseur"""
        self.curseur, success = ((self.curseur + 1, True) if
                                 len(self.texte) > self.curseur
                                 else (self.curseur, False))
        return success

    def recule_curseur(self):
        """avance le curseur"""
        self.curseur, success = ((self.curseur - 1, True) if
                                 self.curseur > 0 else (self.curseur, False))
        return success

    def insert_at(self, char: str):
        """avance le curseur"""
        self.texte.insert(self.curseur, char)
        self.avance_curseur()

    def sup_at(self):
        """supprime le caractère à la position du curseur"""
        success = self.recule_curseur()
        if success: self.texte.pop(self.curseur)

    def newline(self):
        """crée une nouvelle ligne"""
        size = POLICE.size(str(texte)[:texte.curseur])
        init_pos_y: int = (size[0] // (self.max_length))
        pos_y = init_pos_y
        while pos_y - init_pos_y == 0:
            self.insert_at(" ")
            size = POLICE.size(str(texte)[:texte.curseur])
            pos_y: int = (size[0] // (self.max_length))

    def __str__(self) -> str:
        return "".join(self.texte)


# fonctions de surface

def clear():
    """nettoie l'écran"""
    WINDOW.fill("#000000")


def texte_wrapper(texte_surfaces: List[pygame.Surface], pos: Tuple[float, float]):
    """retourne le texte à la ligne"""
    height = texte_surfaces[0].get_height()
    return ((surf, (pos[0], pos[1] + k * height)) for k, surf in enumerate(texte_surfaces))


def split_surface(surface: pygame.Surface, max_length: int):
    """découpe une longue surface selon le paramètre max_length"""
    liste_surface: List[pygame.Surface] = [pygame.Surface((max_length, surface.get_height()))
                                           for _ in range(surface.get_width() // max_length + 1)]

    for k, surf in enumerate(liste_surface):
        surf.blit(surface, (-k * max_length, 0))
    return liste_surface


def render_texte(texte: str, max_length: int):
    """affiche le texte"""
    return split_surface(POLICE.render(texte, True, "#30FF00"), max_length)


def render_curseur(texte_surfaces: List[pygame.Surface], pos: Tuple[int, int], max_length: int):
    """affiche le curseur"""
    surf = pygame.Surface((1, texte_surfaces[0].get_height()))
    surf.fill("#FFFFFF")
    size = POLICE.size(str(texte)[:texte.curseur])
    position = (pos[0] + size[0] % (max_length), pos[1] +
                (size[0] // (max_length)) * size[1])
    return surf, position


# main loop

def main():
    """boucle principale"""
    running = True

    Application.current_app = shell
    bureaux.get_focus()

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

# variables

texte = Texte(100)
shell = Shell('ressources/icons/cmd.png', [pygame.KEYDOWN])
bureaux = Desktop('ressources/background/desktop.jpg', 'ressources/icons/bureaux.png',
                  [Link(shell, 'ressources/icons/cmd.png', (100, 100), 0.5)], [pygame.MOUSEBUTTONDOWN])

# appel de la fonction principale

main()
