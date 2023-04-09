import pygame

pygame.init()

class Text:

    def __init__(self, texte: str, police: pygame.font.Font) -> None:
        self.police = police
        self.texte = texte
        self.curseur = 0

    def avance(self):
        if self.curseur < len(self.texte) - 1:
            self.curseur += 1

    def recule(self):
        if self.curseur > 0:
            self.curseur -= 1


text = Text('abcdef12345678987654321\nghijklm', pygame.font.SysFont('Arial', 20))
threshold = 100
WINDOW = pygame.display.set_mode((600, 600))

def render():
    posx = 0
    posy = 0

    for rang, lettre in enumerate(text.texte):
        if rang == text.curseur:
            curseur_surface = pygame.Surface((2, 20))
            curseur_surface.fill('#FFFFFF')

            WINDOW.blit(curseur_surface, (posx, posy))

        if lettre == '\n':
            posy += 20
            posx = 0

        else:
            surface = text.police.render(lettre, True, '#FFFFFF')
            if posx + surface.get_width() > threshold:
                posx = 0
                posy += 20

            WINDOW.blit(surface, (posx, posy))
            posx += surface.get_width()

while True:
    WINDOW.fill('#000000')
    for event in pygame.event.get():
        match event.type:
            case pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    text.recule()
                elif event.key == pygame.K_RIGHT:
                    text.avance()
            case _:
                ...
    render()
    pygame.display.flip()
