import random
from typing import Optional, Tuple, List
from engine.ai.base_ai import BaseAI
from engine.movement import Movement
from engine.pawn import Pawn
import engine.victory as victory


class AdvancedAI(BaseAI):
    def __init__(self, team: str = "RED"):
        super().__init__(team)
        if self.team == "RED":
            self.opponent_team = "BLUE" 
        else:
            self.opponent_team = "RED"

    def _get_target_pattern_cells(self, game) -> List[Tuple[int, int]]:
        offset = (game.board.size - game.pattern.size) // 2
        cells = []
        for r in range(game.pattern.size):
            for c in range(game.pattern.size):
                if game.pattern.grid[r][c] == 1:
                    cells.append((r + offset, c + offset))
        return cells

    def _evaluate_static_board(self, game, target_cells: List[Tuple[int, int]]) -> float:
        """Heuristic board evaluation from the perspective of this AI."""
        ai_player = game.red if self.team == "RED" else game.blue
        human_player = game.blue if self.team == "RED" else game.red

        if victory.check_victory(game, ai_player):
            return 10000.0
        if victory.check_victory(game, human_player):
            return -10000.0

        ai_pattern_count = 0
        human_pattern_count = 0

        for r, c in target_cells:
            pawn = game.board.get_pawn(r, c)
            if pawn is not None:
                if pawn.team == self.team:
                    ai_pattern_count += 1
                else:
                    human_pattern_count += 1

        # Base pattern differential
        score = (ai_pattern_count * 200.0) - (human_pattern_count * 250.0)

        # Respawn attrition advantage
        score += (human_player.captures_suffered * 15.0) - (ai_player.captures_suffered * 20.0)

        # Proximity advantage for AI pieces towards empty pattern cells
        empty_targets = [
            (tr, tc) for tr, tc in target_cells
            if game.board.get_pawn(tr, tc) is None or game.board.get_pawn(tr, tc).team != self.team
        ]

        if empty_targets:
            for pawn in ai_player.pawns:
                if pawn.active and (pawn.row, pawn.col) not in target_cells:
                    min_dist = min(abs(pawn.row - tr) + abs(pawn.col - tc) for tr, tc in empty_targets)
                    score -= min_dist * 1.5

        return score

    def _simulate_move(self, game, pawn: Pawn, target_row: int, target_col: int):
        """Simulates a move on the board and returns undo data."""
        old_row, old_col = pawn.row, pawn.col
        captured = game.board.get_pawn(target_row, target_col)

        # Apply move
        game.board.grid[old_row][old_col] = None
        pawn.row, pawn.col = target_row, target_col
        game.board.grid[target_row][target_col] = pawn

        if captured is not None:
            captured.active = False

        return old_row, old_col, captured

    def _undo_move(self, game, pawn: Pawn, old_row: int, old_col: int, target_row: int, target_col: int, captured: Optional[Pawn]):
        """Restores the board state after simulation."""
        game.board.grid[target_row][target_col] = captured
        pawn.row, pawn.col = old_row, old_col
        game.board.grid[old_row][old_col] = pawn

        if captured is not None:
            captured.active = True

    def _evaluate_human_chance_node(self, game, target_cells: List[Tuple[int, int]]) -> float:
        """Calculates expected score across all 6 human dice rolls."""
        human_player = game.blue if self.team == "RED" else game.red
        expected_score = 0.0

        for d in range(1, 7):
            game.dice.value = d
            min_score = float("inf")
            has_move = False

            for pawn in human_player.pawns:
                if not pawn.active:
                    continue
                valid_moves = Movement.get_valid_moves_for_pawn(game, pawn)
                for tr, tc in valid_moves:
                    has_move = True
                    old_r, old_c, cap = self._simulate_move(game, pawn, tr, tc)
                    board_eval = self._evaluate_static_board(game, target_cells)
                    self._undo_move(game, pawn, old_r, old_c, tr, tc, cap)

                    if board_eval < min_score:
                        min_score = board_eval

            if not has_move:
                # Human had no moves on this roll
                min_score = self._evaluate_static_board(game, target_cells)

            expected_score += (1.0 / 6.0) * min_score

        return expected_score

    def select_move(self, game) -> Optional[Tuple[Pawn, int, int]]:
        ai_player = game.red if self.team == "RED" else game.blue
        target_cells = self._get_target_pattern_cells(game)

        best_score = float("-inf")
        best_action = None
        current_dice = game.dice.value

        for pawn in ai_player.pawns:
            if not pawn.active:
                continue

            game.dice.value = current_dice
            valid_moves = Movement.get_valid_moves_for_pawn(game, pawn)

            for target_row, target_col in valid_moves:
                # 1. Immediate victory check
                old_r, old_c, cap = self._simulate_move(game, pawn, target_row, target_col)
                if victory.check_victory(game, ai_player):
                    self._undo_move(
                        game,
                        pawn,
                        old_r,
                        old_c,
                        target_row,
                        target_col,
                        cap
                    )

                    # Human-response simulation may have changed the dice value
                    # during evaluation of an earlier candidate move.
                    game.dice.value = current_dice

                    return (pawn, target_row, target_col)

                # 2. Expectiminimax evaluation over human response
                move_score = self._evaluate_human_chance_node(game, target_cells)
                self._undo_move(game, pawn, old_r, old_c, target_row, target_col, cap)

                # Add small tiebreaker
                move_score += random.uniform(0.0, 0.5)

                if move_score > best_score:
                    best_score = move_score
                    best_action = (pawn, target_row, target_col)

        # Restore actual dice value
        game.dice.value = current_dice
        return best_action