import random
from typing import Optional, Tuple, List
from engine.ai.base_ai import BaseAI
from engine.movement import Movement
from engine.pawn import Pawn


class LearningAI(BaseAI):
    def __init__(self, team: str = "RED"):
        super().__init__(team)
        self.human_moves_count = 0
        self.human_captures_count = 0
        self.human_pattern_moves = 0

    def _get_target_pattern_cells(self, game) -> List[Tuple[int, int]]:
        offset = (game.board.size - game.pattern.size) // 2
        cells = []
        for r in range(game.pattern.size):
            for c in range(game.pattern.size):
                if game.pattern.grid[r][c] == 1:
                    cells.append((r + offset, c + offset))
        return cells

    def record_human_move(self, game, from_pos: Tuple[int, int], to_pos: Tuple[int, int], was_capture: bool):
        """call when human finished the turn."""
        self.human_moves_count += 1
        if was_capture:
            self.human_captures_count += 1

        target_cells = self._get_target_pattern_cells(game)
        if to_pos in target_cells:
            self.human_pattern_moves += 1

    def _get_dynamic_weights(self) -> Tuple[float, float, float]:
        """ Returns (pattern_weight, capture_weight, proximity_weight) based on observed human behavior."""
        if self.human_moves_count < 2:
            return 100.0, 40.0, 2.0  # Default balanced baseline

        aggression_ratio = self.human_captures_count / self.human_moves_count
        pattern_ratio = self.human_pattern_moves / self.human_moves_count

        # if human is hyper-aggressive -> the AI prioritizes pattern-rush to win fast
        if aggression_ratio > 0.35:
            return 140.0, 25.0, 3.5

        # if human is rushing the pattern -> AI plays disruptor to capture & drain respawns
        if pattern_ratio > 0.40:
            return 80.0, 75.0, 2.0

        return 100.0, 45.0, 2.5

    def _evaluate_move(
        self,
        game,
        pawn: Pawn,
        target_row: int,
        target_col: int,
        target_cells: List[Tuple[int, int]],
        weights: Tuple[float, float, float]
    ) -> float:
        pattern_w, capture_w, prox_w = weights
        score = 0.0

        # Pattern tile occupation
        if (target_row, target_col) in target_cells:
            score += pattern_w

        # Capture reward
        target_pawn = game.board.get_pawn(target_row, target_col)
        if target_pawn is not None and target_pawn.team != self.team:
            score += capture_w

        # Proximity reward
        unfilled_targets = [
            (tr, tc) for tr, tc in target_cells
            if game.board.get_pawn(tr, tc) is None or game.board.get_pawn(tr, tc).team != self.team
        ]

        if unfilled_targets:
            min_dist = min(
                abs(target_row - tr) + abs(target_col - tc)
                for tr, tc in unfilled_targets
            )
            score -= min_dist * prox_w

        # Small tie-breaker
        score += random.uniform(0.0, 1.0)
        return score

    def select_move(self, game) -> Optional[Tuple[Pawn, int, int]]:
        player = game.red if self.team == "RED" else game.blue
        target_cells = self._get_target_pattern_cells(game)
        weights = self._get_dynamic_weights()

        best_score = float("-inf")
        best_action = None

        for pawn in player.pawns:
            if not pawn.active:
                continue

            valid_moves = Movement.get_valid_moves_for_pawn(game, pawn)
            for row, col in valid_moves:
                score = self._evaluate_move(game, pawn, row, col, target_cells, weights)
                if score > best_score:
                    best_score = score
                    best_action = (pawn, row, col)

        return best_action