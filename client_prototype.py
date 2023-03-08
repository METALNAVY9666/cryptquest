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

    def __init__(self, texte_renderer: 'TextRenderer', interpreter: 'Interpreter', icon_nom: str, event_liste: List[int]) -> None:
        super().__init__(icon_nom, event_liste)
        self.texte_renderer = texte_renderer
        self.interpreter = interpreter
        self.prefix = "C:/> "

        # initialisation de la ligne de commande
        self.add_prefix()
        self.texte_renderer.texte.register()

    def add_prefix(self):
        """ajoute un préfix au début d'une ligne"""
        self.texte_renderer.texte.insert_texte_at(self.prefix)

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
                self.texte_renderer.texte.recule_curseur()
            case pygame.K_RIGHT:
                self.texte_renderer.texte.avance_curseur()
            case pygame.K_BACKSPACE:
                self.texte_renderer.texte.sup_at()
            case pygame.K_DELETE:
                self.texte_renderer.texte.vide()
            case pygame.K_RETURN:
                self.interpreter.execute(self.texte_renderer.texte.get_texte())
                self.texte_renderer.texte.newline()
                self.add_prefix()
                self.texte_renderer.texte.register()
            case _:
                lettre = event.unicode
                self.texte_renderer.texte.insert_at(lettre)

    def update(self):
        """mise à jour"""
        texte_surfaces = self.texte_renderer.render_texte(str(self.texte_renderer.texte),
                                                          self.texte_renderer.texte.max_length)
        blit_sequence: Any = self.texte_renderer.texte_wrapper(texte_surfaces)
        WINDOW.blits(blit_sequence)
        WINDOW.blit(*self.texte_renderer.render_curseur(texte_surfaces))


class Desktop(Application):
    """gestion des bureaux"""

    def __init__(self, background_nom: str, icon_nom: str, links: List[Link], event_liste: List[int]) -> None:
        super().__init__(icon_nom, event_liste)
        self.background = pygame.transform.scale(
            pygame.image.load(background_nom), WINDOW.get_size())

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


class Interpreter:
    def __init__(self, texte: 'Texte') -> None:
        self.texte = texte

    def execute(self, commande: str):
        """exécute une commande donnée"""
        # cas de commande vide
        if commande == "":
            return
        
        # on commence par passer à la ligne suivante
        self.texte.newline()

        # on traite ensuite les différentes commandes
        commande = commande.strip()
        tokens = commande.split(" ")
        match tokens[0]:
            case 'cd':
                self.texte.insert_texte_at('C:')
            case _:
                self.texte.insert_texte_at('Commande non reconnue')

        # saut de ligne de fin d'exécution
        self.texte.newline()


class TextRenderer:
    def __init__(self, texte: 'Texte', pos: Tuple[float, float]):
        self.pos = pos
        self.texte = texte

    def texte_wrapper(self, texte_surfaces: List[pygame.Surface]):
        """retourne le texte à la ligne"""
        height = texte_surfaces[0].get_height()
        return ((surf, (self.pos[0], self.pos[1] + k * height)) for k, surf in enumerate(texte_surfaces))

    def split_surface(self, surface: pygame.Surface):
        """découpe une longue surface selon le paramètre max_length"""
        liste_surface: List[pygame.Surface] = [pygame.Surface((self.texte.max_length, surface.get_height()))
                                               for _ in range(surface.get_width() // self.texte.max_length + 1)]

        for k, surf in enumerate(liste_surface):
            surf.blit(surface, (-k * self.texte.max_length, 0))
        return liste_surface

    def render_texte(self, texte: str, max_length: int):
        """affiche le texte"""
        return self.split_surface(POLICE.render(str(self.texte), True, "#30FF00"))

    def render_curseur(self, texte_surfaces: List[pygame.Surface]):
        """affiche le curseur"""
        surf = pygame.Surface((1, texte_surfaces[0].get_height()))
        surf.fill("#FFFFFF")
        size = POLICE.size(
            str(self.texte)[:self.texte.curseur + len(self.texte.pre_texte)])
        position = (self.pos[0] + size[0] % (self.texte.max_length), self.pos[1] +
                    (size[0] // (self.texte.max_length)) * size[1])
        return surf, position


class Texte:
    def __init__(self, max_length: int) -> None:
        self.curseur: int = 0
        self.texte: List[str] = []
        self.pre_texte: List[str] = []
        self.max_length = max_length

    def avance_curseur(self):
        """avance le curseur"""
        self.curseur = (self.curseur + 1 if
                        len(self.texte) + len(self.pre_texte) > self.curseur
                        else self.curseur)

    def recule_curseur(self):
        """avance le curseur"""
        self.curseur = (self.curseur - 1 if
                        self.curseur > len(self.pre_texte) else self.curseur)

    def insert_at(self, char: str):
        """insère un caractère"""
        self.texte.insert(self.curseur, char)
        self.avance_curseur()

    def insert_texte_at(self, texte: str):
        """insère un texte"""
        for char in texte:
            self.insert_at(char)

    def sup_at(self):
        """supprime le caractère à la position du curseur"""
        self.recule_curseur()
        if len(self.texte) > 0:
            self.texte.pop(self.curseur - len(self.pre_texte))

    def vide(self):
        """vide le texte"""
        self.texte.clear()

    def register(self):
        """enregistre le texte courant dans pre_texte"""
        self.pre_texte += self.texte
        self.vide()

    def newline(self):
        """crée une nouvelle ligne"""
        size = POLICE.size(str(self)[:self.curseur + len(self.pre_texte)])
        init_pos_y: int = (size[0] // (self.max_length))
        pos_y = init_pos_y
        while pos_y - init_pos_y == 0:
            self.insert_at(" ")
            size = POLICE.size(str(self)[:self.curseur + len(self.pre_texte)])
            pos_y: int = (size[0] // (self.max_length))

    def __str__(self) -> str:
        return "".join(self.pre_texte + self.texte)

    def get_texte(self) -> str:
        return "".join(self.texte)


# fonctions de surface

def clear():
    """nettoie l'écran"""
    WINDOW.fill("#000000")


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


text = Texte(600)
texte_renderer = TextRenderer(text, (100, 100))
interpreter = Interpreter(text)
shell = Shell(texte_renderer, interpreter,
              'ressources/icons/cmd.png', [pygame.KEYDOWN])
bureaux = Desktop('ressources/background/desktop.jpg', 'ressources/icons/bureaux.png',
                  [Link(shell, 'ressources/icons/cmd.png', (100, 100), 0.5)], [pygame.MOUSEBUTTONDOWN])

# appel de la fonction principale

main()
