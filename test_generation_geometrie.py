import pygame

pygame.init()


WINDOW = pygame.display.set_mode((600, 600))


def intersect(surface1: pygame.Surface, surface2: pygame.Surface):
    """interesction"""
    mask1 = pygame.mask.from_surface(surface1)
    mask2 = pygame.mask.from_surface(surface2)

    intersection = mask1.overlap_mask(mask2, (0, 0))

    return intersection.to_surface(surface=pygame.Surface((30, 30), pygame.SRCALPHA),
                                   setsurface=surface2, unsetcolor=None)


shape1 = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.rect(shape1, '#FFFFFF', pygame.Rect(5, 5, 20, 20))

shape2 = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.circle(shape2, '#FFFFFF', (15, 15), 10)

vide = pygame.Surface((30, 30), pygame.SRCALPHA)

for x in range(30):
    for y in range(30):
        if not (x + y) % 4:
            vide.set_at((x, y), "#FF00FF")


while True:
    WINDOW.blit(shape1, (100, 100))
    WINDOW.blit(intersect(shape2, vide), (100, 100))

    pygame.display.flip()