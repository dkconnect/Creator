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

    def roll_dice(self):
        return self.dice.roll()
