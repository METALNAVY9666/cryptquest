import pygame

pygame.init()


WINDOW = pygame.display.set_mode((600, 600))


valeur = [(0, 2, 0), (2, 0, 4), (1, 1, 0)]


def intersect(surface1: pygame.Surface, surface2: pygame.Surface):
    """interesction"""
    mask1 = pygame.mask.from_surface(surface1)
    mask2 = pygame.mask.from_surface(surface2)

    intersection = mask1.overlap_mask(mask2, (0, 0))

    return intersection.to_surface(surface=pygame.Surface(intersection.get_size(), pygame.SRCALPHA),
                                   setsurface=surface2, unsetcolor=None)


shape1 = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.rect(shape1, '#FFFFFF', pygame.Rect(5, 5, 20, 20))

shape2 = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.circle(shape2, '#FFFFFF', (15, 15), 9)

shape3 = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.polygon(shape3, '#FFFFFF', [(5, 5), (15, 25), (25, 5)])

shape4 = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.polygon(shape4, '#FFFFFF', [(10, 0), (20, 0), (20, 30), (10, 30)])

shapes = [shape1, shape2, shape3, shape4]

raye = pygame.Surface((30, 30), pygame.SRCALPHA)

for x in range(30):
    for y in range(30):
        if not (x + y) % 3:
            raye.set_at((x, y), "#FF00FF")

vide = pygame.Surface((30, 30), pygame.SRCALPHA)
vide.fill('#000000')

plein = pygame.Surface((30, 30), pygame.SRCALPHA)
plein.fill('#00FF00')

contenu = [raye, vide, plein]

while True:
    for val in valeur:
        surf = intersect(shapes[val[0]], contenu[val[1]])
        surf = pygame.transform.rotate(surf, val[2] * 45)
        WINDOW.blit(surf, (100, 100))



    pygame.display.flip()