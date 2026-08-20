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
        self.current_player = self.blue
        self.selected_pawn = None
        self.game_over = False
        self.winner = None

        self.create_pawns()
        print(self.pattern.name)

    def create_pawns(self):
        pawn_id = 0

        # Blue Pawns Creation
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

        # Red Pawns Creatin
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

        # From the 11th loss onward, the pawn will be permanently removed.
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
        if self.game_over:
            return False
        if self.dice.value is None:
            return False

        pawn = self.board.get_pawn(row, col)
        
        if pawn is None:
            self.selected_pawn = None
            return False

        if pawn.team != self.current_player.team:
            return False

        self.selected_pawn = pawn
        return True
    
    def get_valid_moves(self):
        return Movement.get_valid_moves(self)

    def move_selected_pawn(self, row, col):
        if self.game_over:
            return False
        if self.selected_pawn is None:
            return False

        if (row, col) not in self.get_valid_moves():
            return False

        pawn = self.selected_pawn

        captured_pawn = self.board.get_pawn(row, col)

        self.board.grid[pawn.row][pawn.col] = None

        # Move the pawn
        pawn.row = row
        pawn.col = col
        self.board.grid[row][col] = pawn
        
        Capture.handle_capture(self, captured_pawn)

        if victory.check_victory(self, self.current_player):
            self.game_over = True
            self.winner = self.current_player
            return True

        self.selected_pawn = None

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
        if self.game_over:
            return None
        if self.dice.value is not None:
            return self.dice.value

        return self.dice.roll()
