import pygame


class Renderer:
    CELL_SIZE = 48
    BOARD_X = 40
    BOARD_Y = 40

    def __init__(self, screen, game):
        self.screen = screen
        self.game = game

    def draw(self):
        self.screen.fill((30, 30, 30))

        # Draw board
        for row in range(self.game.board.size):
            for col in range(self.game.board.size):
                x = self.BOARD_X + col * self.CELL_SIZE
                y = self.BOARD_Y + row * self.CELL_SIZE

                rect = pygame.Rect(
                    x,
                    y,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )

                pygame.draw.rect(
                    self.screen,
                    (220, 220, 220),
                    rect,
                    1
                )

        # Draw pawns
        for row in range(self.game.board.size):
            for col in range(self.game.board.size):

                pawn = self.game.board.get_pawn(row, col)

                if pawn is None:
                    continue

                x = self.BOARD_X + col * self.CELL_SIZE + self.CELL_SIZE // 2
                y = self.BOARD_Y + row * self.CELL_SIZE + self.CELL_SIZE // 2

                if pawn.team == "BLUE":
                    color = (50, 120, 255)
                else:
                    color = (220, 60, 60)

                pygame.draw.circle(
                    self.screen,
                    color,
                    (x, y),
                    self.CELL_SIZE // 2 - 4
                )

                if pawn == self.game.selected_pawn:
                    pygame.draw.circle(
                        self.screen,
                        (255, 255, 0),
                        (x, y),
                        self.CELL_SIZE // 2 - 2,
                        3
                    )
        
        
