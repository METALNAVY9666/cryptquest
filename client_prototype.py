import pygame
from typing import List, Tuple, Any

pygame.init()

# constantes

WINDOW = pygame.display.set_mode((800, 640), pygame.RESIZABLE)
POLICE = pygame.font.Font(
    'ressources/fonts/sourcecodepro.ttf', 16)  # font à changer
POLICE.bold = True

# fonctions de maniment de texte


class Texte:
    def __init__(self) -> None:
        self.curseur: int = 0
        self.texte: List[str] = []

    def avance_curseur(self):
        """avance le curseur"""
        self.curseur = self.curseur + \
            1 if len(self.texte) > self.curseur else self.curseur

    def recule_curseur(self):
        """avance le curseur"""
        self.curseur = self.curseur - 1 if self.curseur > 0 else self.curseur

    def insert_at(self, char: str):
        """avance le curseur"""
        self.texte.insert(self.curseur, char)
        self.avance_curseur()

    def sup_at(self):
        """supprime le caractère à la position du curseur"""
        self.recule_curseur()
        self.texte.pop(self.curseur)

    def __str__(self) -> str:
        return "".join(self.texte)


def update_texte(event: pygame.event.Event):
    """met à jour correctement le texte selon l'entrée de l'utilisateur"""
    match event.key:
        case pygame.K_ESCAPE:
            ...
        case pygame.K_LEFT:
            texte.recule_curseur()
        case pygame.K_RIGHT:
            texte.avance_curseur()
        case pygame.K_BACKSPACE:
            texte.sup_at()
        case _:
            lettre = event.unicode
            texte.insert_at(lettre)


# fonctions de surface


def update():
    """fonction de mise à jour"""
    texte_surfaces = render_texte(str(texte), 100)
    blit_sequence: Any = texte_wrapper(texte_surfaces, (100, 100))
    WINDOW.blits(blit_sequence)
    WINDOW.blit(*render_curseur(texte_surfaces, (100, 100), 100))


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
    position = (pos[0] + size[0] % max_length, pos[1] + (size[0] // max_length) * size[1])
    return surf, position


# main loop

def main():
    """boucle principale"""
    running = True

    while running:
        events = pygame.event.get()
        for evnt in events:
            match evnt.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    update_texte(evnt)
                case _:
                    ...

        update()

        pygame.display.flip()

# variables


texte = Texte()

# appel de la fonction principale

main()
