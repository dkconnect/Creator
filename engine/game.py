from engine.board import Board
from engine.pawn import Pawn
from engine.player import Player
from engine.dice import Dice


class Game:
    def __init__(self):
        self.board = Board()

        self.blue = Player(team="BLUE")
        self.red = Player(team="RED")
        self.dice = Dice()

        self.current_player = self.blue
        self.selected_pawn = None

        self.create_pawns()

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
        if self.dice.value is None:
            return False

        pawn = self.board.get_pawn(row, col)

        if pawn is None:
            self.selected_pawn = None
            return False

        if pawn.team != self.current_player.team:
            self.selected_pawn = None
            return False

        self.selected_pawn = pawn
        return True
    
    def get_valid_moves(self):
        if self.selected_pawn is None:
            return []

        moves = []

        directions = [
            (-1, 0),   # Up
            (1, 0),    # Down
            (0, -1),   # Left
            (0, 1),    # Right
            (-1, -1),  # Up Left
            (-1, 1),   # Up Right
            (1, -1),   # Down Left
            (1, 1)     # Down Right
        ]

        distance = self.dice.value
        pawn = self.selected_pawn

        for dr, dc in directions:
            row = pawn.row + dr * distance
            col = pawn.col + dc * distance

            if not (0 <= row < self.board.size and 0 <= col < self.board.size):
                continue

            target = self.board.get_pawn(row, col)

            if target is not None and target.team == pawn.team:
                continue

            moves.append((row, col))

        return moves

    def move_selected_pawn(self, row, col):
        if self.selected_pawn is None:
            return False

        if (row, col) not in self.get_valid_moves():
            return False

        pawn = self.selected_pawn

        target = self.board.get_pawn(row, col)

        if target is not None:
            self.respawn_pawn(target)

        self.board.grid[pawn.row][pawn.col] = None

        pawn.row = row
        pawn.col = col

        self.board.grid[row][col] = pawn

        self.selected_pawn = None

        self.dice.value = None

        return True

    def roll_dice(self):
        return self.dice.roll()
