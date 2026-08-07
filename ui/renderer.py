import pygame


class Renderer:
    CELL_SIZE = 48
    BOARD_X = 40
    BOARD_Y = 40

    def __init__(self, screen, board):
        self.screen = screen
        self.board = board

    def draw(self):
        self.screen.fill((30, 30, 30))

        for row in range(self.board.size):
            for col in range(self.board.size):
                x = self.BOARD_X + col * self.CELL_SIZE
                y = self.BOARD_Y + row * self.CELL_SIZE

                rect = pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)

                pygame.draw.rect(self.screen, (220, 220, 220), rect, 1)
