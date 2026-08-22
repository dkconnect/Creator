from engine.board import Board
from engine.pawn import Pawn
from engine.player import Player
from engine.dice import Dice
from engine.movement import Movement
from engine.capture import Capture
from engine.pattern import Pattern
import engine.victory as victory

class Game:
    WAITING_FOR_ROLL = "WAITING_FOR_ROLL"
    WAITING_FOR_SELECTION = "WAITING_FOR_SELECTION"
    WAITING_FOR_MOVE = "WAITING_FOR_MOVE"

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
        self.turn_phase = self.WAITING_FOR_ROLL

        self.create_pawns()
        print(self.pattern.name)
            
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

        # Every capture
        player.captures_suffered += 1

        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.grid[r][c] is pawn:
                    self.board.grid[r][c] = None

        # 11th capture permanently removes the pawn
        if player.captures_suffered > 10:
            pawn.active = False
            pawn.row = -1
            pawn.col = -1

            if pawn in player.reserve:
                player.reserve.remove(pawn)

            return False

        if pawn.team == "BLUE":
            spawn_rows = range(2)
        else:
            spawn_rows = range(self.board.size - 2, self.board.size)

        #first empty squar
        for row in spawn_rows:
            for col in range(self.board.size):
                if self.board.get_pawn(row, col) is None:
                    pawn.row = row
                    pawn.col = col
                    pawn.active = True
                    self.board.place_pawn(pawn)

                    # Only successful respawns count.
                    player.respawns += 1

                    return True

        pawn.active = False
        pawn.row = -1
        pawn.col = -1

        if pawn not in player.reserve:
            player.reserve.append(pawn)

        return False
        
    def process_reserve(self, player):
        if not player.reserve:
            return False

        # No more respawns after the 10th allowed respawn.
        if player.respawns >= 10:
            for pawn in player.reserve:
                pawn.active = False
                pawn.row = -1
                pawn.col = -1

            player.reserve.clear()
            return False

        if player.team == "BLUE":
            spawn_rows = range(2)
        else:
            spawn_rows = range(self.board.size - 2, self.board.size)

        # Oldest reserved pawn first.
        pawn = player.reserve[0]

        # Find first empty spawn square.
        for row in spawn_rows:
            for col in range(self.board.size):
                if self.board.get_pawn(row, col) is None:
                    player.reserve.pop(0)

                    pawn.row = row
                    pawn.col = col
                    pawn.active = True

                    self.board.place_pawn(pawn)

                    player.respawns += 1

                    return True

        return False

    def select_pawn(self, row, col):
        if self.game_over:
            return False

        if self.turn_phase != self.WAITING_FOR_SELECTION:
            return False

        pawn = self.board.get_pawn(row, col)

        # Clicked empty square.
        if pawn is None:
            self.selected_pawn = None
            return False

        if not pawn.active:
            return False

        # Clicked opponent pawn.
        if pawn.team != self.current_player.team:
            return False

        # Select own pawn.
        self.selected_pawn = pawn
        self.turn_phase = self.WAITING_FOR_MOVE

        return True
    
    def get_valid_moves(self):
        return Movement.get_valid_moves(self)

    def move_selected_pawn(self, row, col):
        if self.game_over:
            return False

        if self.turn_phase != self.WAITING_FOR_MOVE:
            return False

        if self.selected_pawn is None:
            return False

        if (row, col) not in self.get_valid_moves():
            return False

        pawn = self.selected_pawn

        captured_pawn = self.board.get_pawn(row, col)

        # Remember the old position.
        old_row = pawn.row
        old_col = pawn.col

        # Remove moving pawn from its old position.
        self.board.grid[old_row][old_col] = None

        # Move the pawn.
        pawn.row = row
        pawn.col = col
        self.board.grid[row][col] = pawn

        # A spawn square may now be available.
        # Handle captured pawn.
        Capture.handle_capture(self, captured_pawn)

        # A spawn square may now be available for the captured pawn's team.
        if captured_pawn is not None:
            captured_player = (
                self.blue if captured_pawn.team == "BLUE" else self.red
            )
            self.process_reserve(captured_player)

        if victory.check_victory(self, self.current_player):
            self.game_over = True
            self.winner = self.current_player
            self.turn_phase = None
            return True

        # Clear selection
        self.selected_pawn = None

        # Reset dice
        self.dice.value = None

        self.switch_turn()

        self.turn_phase = self.WAITING_FOR_ROLL

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

        self.selected_pawn = None
        self.dice.value = None
        self.turn_phase = self.WAITING_FOR_ROLL

    def roll_dice(self):
        if self.game_over:
            return None

        if self.turn_phase != self.WAITING_FOR_ROLL:
            return None

        value = self.dice.roll()

        if not Movement.player_has_legal_move(
            self,
            self.current_player
        ):
            # No legal move: automatically skip the turn.
            self.switch_turn()
            return value

        self.turn_phase = self.WAITING_FOR_SELECTION

        return value
