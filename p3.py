import pygame
import sys
import time

pygame.init()

pygame.display.set_mode((720, 480))

surface = pygame.display.get_surface()

surface.fill((255,255,255))
pygame.draw.circle(surface,(225,0,0),(150,200),40,4)

cnt = 0
last_time = time.time()

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(event)
    
    cnt += 1
    
    if cnt % 1000 == 0:
        current_time = time.time()
        print(1000/(current_time - last_time))
        last_time = current_time
    
    pygame.display.update()