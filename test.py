import pygame

pygame.init()

WINDOW = pygame.display.set_mode((600, 600))

while True:
    for event in pygame.event.get():
        print(event)
    print(pygame.key.get_pressed()[21])