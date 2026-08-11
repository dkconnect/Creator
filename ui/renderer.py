import pygame


class Renderer:
    CELL_SIZE = 48
    BOARD_X = 40
    BOARD_Y = 40

    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.font = pygame.font.SysFont("arial", 28)

    def draw(self):
        self.screen.fill((30, 30, 30))

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

        pattern = self.game.pattern

        offset = (self.game.board.size - pattern.size) // 2

        for row in range(pattern.size):
            for col in range(pattern.size):

                if pattern.grid[row][col] == 0:
                    continue

                x = self.BOARD_X + (col + offset) * self.CELL_SIZE
                y = self.BOARD_Y + (row + offset) * self.CELL_SIZE

                rect = pygame.Rect(
                    x,
                    y,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )

                pygame.draw.rect(
                    self.screen,
                    (90, 90, 90),
                    rect
                )

        for row, col in self.game.get_valid_moves():
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
                (0, 200, 0),
                rect,
                3
            )

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

        turn_text = self.font.render(
            f"Turn : {self.game.current_player.team}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(turn_text, (860, 60))

        dice_value = self.game.dice.value

        if dice_value is None:
            dice_string = "-"
        else:
            dice_string = str(dice_value)

        dice_text = self.font.render(
            f"Dice : {dice_string}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(dice_text, (860, 110))

        pattern_text = self.font.render(
            f"Pattern : {self.game.pattern.name}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(pattern_text, (860, 160))
        
        
