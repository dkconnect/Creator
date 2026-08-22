import pygame
from engine.board import Board
from engine.pawn import Pawn
from engine.player import Player
from engine.dice import Dice
from engine.movement import Movement
from engine.capture import Capture
from engine.pattern import Pattern
import engine.victory as victory

class Game:
    def __init__(self):
        self.board = Board()

        self.blue = Player(team="BLUE")
        self.red = Player(team="RED")
        self.dice = Dice()
        self.pattern = Pattern()
        self.pattern.load_random()
        self.preview_active = True
        self.preview_start_time = pygame.time.get_ticks()
        self.preview_revealed_cells = 0
        self.current_player = self.blue
        self.selected_pawn = None
        self.game_over = False
        self.winner = None
        self.preview_fade_start = 2500
        self.preview_duration = 3000

        self.create_pawns()
        print(self.pattern.name)
    
    def update_preview(self):
        if not self.preview_active:
            return

        elapsed = pygame.time.get_ticks() - self.preview_start_time

        total_cells = self.pattern.size * self.pattern.size

        if elapsed < self.preview_fade_start:
            self.preview_revealed_cells = min(
                int((elapsed / self.preview_fade_start) * total_cells),
                total_cells
            )

        if elapsed >= self.preview_duration:
            self.preview_active = False
            
    def create_pawns(self):
        pawn_id = 0

        # Blue pawns
        for row in range(2):
            for col in range(self.board.size):
                pawn = Pawn(
                    id=pawn_id,
                    team="BLUE",
                    row=row,
                    col=col
                )

                self.blue.pawns.append(pawn)
                self.board.place_pawn(pawn)

                pawn_id += 1

        # Red pawns
        for row in range(self.board.size - 2, self.board.size):
            for col in range(self.board.size):
                pawn = Pawn(
                    id=pawn_id,
                    team="RED",
                    row=row,
                    col=col
                )

                self.red.pawns.append(pawn)
                self.board.place_pawn(pawn)

                pawn_id += 1

    def respawn_pawn(self, pawn):
        player = self.blue if pawn.team == "BLUE" else self.red

        player.respawns += 1

        # From the 11th loss onward, the pawn is permanently removed.
        if player.respawns > 10:
            pawn.active = False
            return False

        if pawn.team == "BLUE":
            spawn_rows = range(2)
        else:
            spawn_rows = range(self.board.size - 2, self.board.size)

        for row in spawn_rows:
            for col in range(self.board.size):
                if self.board.get_pawn(row, col) is None:
                    pawn.row = row
                    pawn.col = col
                    pawn.active = True
                    self.board.place_pawn(pawn)
                    return True

        return False
    
    def select_pawn(self, row, col):
        if self.preview_active:
            return False
        if self.game_over:
            return False
        if self.dice.value is None:
            return False

        pawn = self.board.get_pawn(row, col)

        # Clicked empty square
        if pawn is None:
            self.selected_pawn = None
            return False
        if not pawn.active:
            return False

        # Clicked opponent pawn
        if pawn.team != self.current_player.team:
            return False

        # Clicked one of your own pawns
        self.selected_pawn = pawn
        return True
    
    def get_valid_moves(self):
        return Movement.get_valid_moves(self)

    def move_selected_pawn(self, row, col):
        if self.preview_active:
            return False
        if self.game_over:
            return False
        if self.selected_pawn is None:
            return False

        if (row, col) not in self.get_valid_moves():
            return False

        pawn = self.selected_pawn

        captured_pawn = self.board.get_pawn(row, col)

        # Remove moving pawn from its old position
        self.board.grid[pawn.row][pawn.col] = None

        # Move the pawn
        pawn.row = row
        pawn.col = col
        self.board.grid[row][col] = pawn

        # Respawn captured pawn after the move
        Capture.handle_capture(self, captured_pawn)

        if victory.check_victory(self, self.current_player):
            self.game_over = True
            self.winner = self.current_player
            return True

        # Clear selection
        self.selected_pawn = None

        # Reset dice
        self.dice.value = None

        self.switch_turn()

        return True
    
    def handle_click(self, row, col):
        if self.selected_pawn is not None:
            if self.move_selected_pawn(row, col):
                return

        self.select_pawn(row, col)

    def switch_turn(self):
        if self.current_player == self.blue:
            self.current_player = self.red
        else:
            self.current_player = self.blue

    def roll_dice(self):
        if self.preview_active:
            return None
        if self.game_over:
            return None
        if self.dice.value is not None:
            return self.dice.value

        return self.dice.roll()
