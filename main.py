from engine.board import Board
from ui.renderer import Renderer
import pygame

pygame.init()

WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Creator")

board = Board()
renderer = Renderer(screen, board)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    renderer.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
