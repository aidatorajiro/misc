import pygame

pygame.init()

pygame.display.set_mode((720, 480))

surface = pygame.display.get_surface()

surface.fill((255,255,255))
pygame.draw.circle(surface,(225,0,0),(150,200),40,4)

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        pass
    pygame.display.update()
    clock.tick(60)