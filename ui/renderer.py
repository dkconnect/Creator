import pygame


class Renderer:
    CELL_SIZE = 48
    BOARD_X = 40
    BOARD_Y = 40

    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.font = pygame.font.SysFont("arial", 28)
        self.dice_button = pygame.Rect(860, 310, 220, 60)
        self.rematch_button = pygame.Rect(390, 500, 200, 60)
        self.menu_button = pygame.Rect(610, 500, 200, 60)

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

        # Draw pattern
        pattern = self.game.pattern

        offset = (self.game.board.size - pattern.size) // 2

        pattern_surface = pygame.Surface(
            (self.CELL_SIZE, self.CELL_SIZE),
            pygame.SRCALPHA
        )

        pattern_surface.fill((255, 255, 255, 40))

        for row in range(pattern.size):
            for col in range(pattern.size):

                if pattern.grid[row][col] != 1:
                    continue

                x = self.BOARD_X + (col + offset) * self.CELL_SIZE
                y = self.BOARD_Y + (row + offset) * self.CELL_SIZE

                self.screen.blit(pattern_surface, (x, y))
        
        # Pawn losses
        blue_losses_text = self.font.render(
            f"Blue Losses : {self.game.blue.respawns}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(blue_losses_text, (860, 210))


        red_losses_text = self.font.render(
            f"Red Losses : {self.game.red.respawns}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(red_losses_text, (860, 260))

        # Draw valid moves
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

        # Current Turn
        turn_text = self.font.render(
            f"Turn : {self.game.current_player.team}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(turn_text, (860, 60))

        # Dice button
        pygame.draw.rect(
            self.screen,
            (70, 70, 70),
            self.dice_button,
            border_radius=8
        )

        button_text = self.font.render(
            "ROLL DICE",
            True,
            (255, 255, 255)
        )

        button_rect = button_text.get_rect(
            center=self.dice_button.center
        )

        self.screen.blit(button_text, button_rect)

        # Dice
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


        # Pattern
        pattern_text = self.font.render(
            f"Pattern : {self.game.pattern.name}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(pattern_text, (860, 160))

        # Victory overlay
        if self.game.game_over:
            overlay = pygame.Surface(
                self.screen.get_size(),
                pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 190))
            self.screen.blit(overlay, (0, 0))

            winner_text = self.font.render(
                f"{self.game.winner.team} WINS!",
                True,
                (255, 255, 255)
            )

            winner_rect = winner_text.get_rect(
                center=(self.screen.get_width() // 2, 420)
            )

            self.screen.blit(winner_text, winner_rect)

            # Rematch button
            pygame.draw.rect(
                self.screen,
                (50, 120, 220),
                self.rematch_button,
                border_radius=8
            )

            rematch_text = self.font.render(
                "REMATCH",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                rematch_text,
                rematch_text.get_rect(center=self.rematch_button.center)
            )

            # Main menu button
            pygame.draw.rect(
                self.screen,
                (70, 70, 70),
                self.menu_button,
                border_radius=8
            )

            menu_text = self.font.render(
                "MAIN MENU",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                menu_text,
                menu_text.get_rect(center=self.menu_button.center)
            )