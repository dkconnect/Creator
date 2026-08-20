from engine.game import Game
from ui.renderer import Renderer
from ui.input_manager import InputManager
import pygame

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
            cell = input_manager.get_clicked_cell(event.pos)

            if cell is not None:
                row, col = cell

                # If a pawn is already selected we move it
                if game.selected_pawn is not None:
                    if game.move_selected_pawn(row, col):
                        print(f"Moved to ({row}, {col})")
                else:
                    if game.select_pawn(row, col):
                        print(f"Selected ({row}, {col})")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                value = game.roll_dice()
                print(f"Dice: {value}")

    renderer.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
