from engine.board import Board
from engine.pawn import Pawn
from engine.player import Player
from engine.dice import Dice
from engine.movement import Movement
from engine.capture import Capture
from engine.pattern import Pattern
from engine.ai.learning_ai import LearningAI
import engine.victory as victory


class Game:
    WAITING_FOR_ROLL = "WAITING_FOR_ROLL"
    WAITING_FOR_SELECTION = "WAITING_FOR_SELECTION"
    WAITING_FOR_MOVE = "WAITING_FOR_MOVE"

    def __init__(self, ai_controller=None):
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
        self.ai_controller = ai_controller

        self.create_pawns()

    def create_pawns(self):
        pawn_id = 0

        # Blue pawns (Rows 0 and 1)
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

        # Red pawns (Rows 14 and 15)
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
        player.captures_suffered += 1

        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.grid[r][c] is pawn:
                    self.board.grid[r][c] = None

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

        for row in spawn_rows:
            for col in range(self.board.size):
                if self.board.get_pawn(row, col) is None:
                    pawn.row = row
                    pawn.col = col
                    pawn.active = True
                    self.board.place_pawn(pawn)
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

        pawn = player.reserve[0]

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

        if self.turn_phase not in (self.WAITING_FOR_SELECTION, self.WAITING_FOR_MOVE):
            return False

        pawn = self.board.get_pawn(row, col)

        if pawn is None or not pawn.active or pawn.team != self.current_player.team:
            return False

        self.selected_pawn = pawn
        self.turn_phase = self.WAITING_FOR_MOVE
        return True

    def get_valid_moves(self):
        return Movement.get_valid_moves(self)

    def get_legal_actions(self, player=None):
        """
        Return every legal pawn move for a player in the current
        game state.

        Each action is represented as:

            (pawn, target_row, target_col)

        This method does not modify the game.
        """

        if self.game_over:
            return []

        if self.dice.value is None:
            return []

        if player is None:
            player = self.current_player

        # Only the current player can have legal actions.
        if player != self.current_player:
            return []

        actions = []

        for pawn in player.pawns:

            if not pawn.active:
                continue

            valid_moves = Movement.get_valid_moves_for_pawn(
                self,
                pawn
            )

            for row, col in valid_moves:
                actions.append(
                    (pawn, row, col)
                )

        return actions

    def move_selected_pawn(self, row, col):
        if self.game_over or self.turn_phase != self.WAITING_FOR_MOVE or self.selected_pawn is None:
            return False

        if (row, col) not in self.get_valid_moves():
            return False

        pawn = self.selected_pawn
        moving_player = self.current_player
        captured_pawn = self.board.get_pawn(row, col)

        old_row, old_col = pawn.row, pawn.col

        # Track human movement for Learning AI
        if isinstance(self.ai_controller, LearningAI) and moving_player.team != self.ai_controller.team:
            self.ai_controller.record_human_move(
                self,
                from_pos=(old_row, old_col),
                to_pos=(row, col),
                was_capture=(captured_pawn is not None)
            )

        # Clear previous cell
        self.board.grid[old_row][old_col] = None

        # Resolve capture on destination
        if captured_pawn is not None:
            Capture.handle_capture(self, captured_pawn)

        # Place pawn
        pawn.row = row
        pawn.col = col
        self.board.grid[row][col] = pawn

        # Reserve processing
        self.process_reserve(moving_player)
        if captured_pawn is not None:
            captured_player = self.blue if captured_pawn.team == "BLUE" else self.red
            self.process_reserve(captured_player)

        # Check victory
        if victory.check_victory(self, moving_player):
            self.game_over = True
            self.winner = moving_player
            self.turn_phase = None
            return True

        self.switch_turn()
        return True

    def handle_click(self, row, col):
        if self.game_over:
            return

        # Ignore human clicks if it's currently an AI turn
        if self.ai_controller is not None and self.current_player.team == self.ai_controller.team:
            return

        target_pawn = self.board.get_pawn(row, col)

        if target_pawn is not None and target_pawn.team == self.current_player.team:
            self.select_pawn(row, col)
            return

        if self.selected_pawn is not None and self.turn_phase == self.WAITING_FOR_MOVE:
            self.move_selected_pawn(row, col)

    def switch_turn(self):
        self.current_player = self.red if self.current_player == self.blue else self.blue
        self.selected_pawn = None
        self.dice.value = None
        self.turn_phase = self.WAITING_FOR_ROLL

    def roll_dice(self):
        if self.game_over or self.turn_phase != self.WAITING_FOR_ROLL:
            return None

        value = self.dice.roll()

        if not Movement.player_has_legal_move(self, self.current_player):
            self.switch_turn()
            return value

        self.turn_phase = self.WAITING_FOR_SELECTION
        return value

    def step_ai(self) -> bool:
        """
        Advances the AI turn by one visible stage so the player can see
        the dice roll before the piece moves.
        Returns True if a full move was completed, False otherwise.
        """
        if self.game_over or self.ai_controller is None:
            return False

        if self.current_player.team != self.ai_controller.team:
            return False

        # Stage 1: Roll the dice (player sees the number)
        if self.turn_phase == self.WAITING_FOR_ROLL:
            self.roll_dice()
            return False  # stop here so the dice value is visible

        # Stage 2: Select and move
        if self.turn_phase == self.WAITING_FOR_SELECTION:
            action = self.ai_controller.select_move(self)
            if action is None:
                self.switch_turn()
                return False

            pawn, tr, tc = action
            if self.select_pawn(pawn.row, pawn.col):
                return self.move_selected_pawn(tr, tc)

        return False