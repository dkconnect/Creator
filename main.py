import pygame
from engine.game import Game
from ui.renderer import Renderer
from ui.input_manager import InputManager

pygame.init()

WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Creator")

game = Game()
renderer = Renderer(screen, game)
input_manager = InputManager(renderer)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if renderer.dice_button.collidepoint(event.pos):
                game.roll_dice()
                continue

            cell = input_manager.get_clicked_cell(event.pos)
            if cell is not None:
                row, col = cell
                game.handle_click(row, col)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game.roll_dice()

    renderer.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
