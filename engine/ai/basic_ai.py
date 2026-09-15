import random
from typing import Optional, Tuple, List
from engine.ai.base_ai import BaseAI
from engine.movement import Movement
from engine.pawn import Pawn


class BasicAI(BaseAI):
    def __init__(self, team: str = "RED"):
        super().__init__(team)

    def _get_target_pattern_cells(self, game) -> List[Tuple[int, int]]:
        offset = (game.board.size - game.pattern.size) // 2
        cells = []
        for r in range(game.pattern.size):
            for c in range(game.pattern.size):
                if game.pattern.grid[r][c] == 1:
                    cells.append((r + offset, c + offset))
        return cells

    def _evaluate_move(
        self,
        game,
        pawn: Pawn,
        target_row: int,
        target_col: int,
        target_cells: List[Tuple[int, int]]
    ) -> float:
        score = 0.0
        progress = 0

        currently_on_pattern = (pawn.row, pawn.col) in target_cells
        landing_on_pattern = (target_row, target_col) in target_cells

        # 1. Highest priority – occupy a pattern cell
        if landing_on_pattern:
            score += 100.0

        # 2. Capture
        target_pawn = game.board.get_pawn(target_row, target_col)
        is_capture = target_pawn is not None and target_pawn.team != self.team
        if is_capture:
            score += 50.0
            # Strong disruption if opponent is on the pattern
            if (target_row, target_col) in target_cells:
                score += 60.0

        # 3. Don’t abandon a pattern cell you already hold
        if currently_on_pattern and not landing_on_pattern and not is_capture:
            score -= 90.0

        # 4. Leave the home rows
        if self.team == "RED":
            home_rows = (14, 15)
        else:
            home_rows = (0, 1)

        if pawn.row in home_rows and target_row not in home_rows:
            score += 15.0

        # 5. Progress toward the pattern
        unfilled_targets = [
            (tr, tc) for tr, tc in target_cells
            if game.board.get_pawn(tr, tc) is None or game.board.get_pawn(tr, tc).team != self.team
        ]

        if unfilled_targets:
            def manhattan(r1, c1, r2, c2):
                return abs(r1 - r2) + abs(c1 - c2)

            current_dist = min(manhattan(pawn.row, pawn.col, tr, tc) for tr, tc in unfilled_targets)
            new_dist = min(manhattan(target_row, target_col, tr, tc) for tr, tc in unfilled_targets)

            progress = current_dist - new_dist
            score += progress * 6.0          # reward getting closer
            score -= new_dist * 1.2          # prefer ending closer

            if current_dist > 6:             # develop far pieces
                score += 5.0

            if is_capture and progress > 0:  # capture while advancing
                score += 20.0

        # 6. Discourage useless moves
        if not is_capture and not landing_on_pattern and progress <= 0:
            score -= 10.0

        # Tiny random factor so it doesn’t always play the exact same move
        score += random.uniform(0.0, 0.8)

        return score
        
    def select_move(self, game) -> Optional[Tuple[Pawn, int, int]]:
        player = game.red if self.team == "RED" else game.blue
        target_cells = self._get_target_pattern_cells(game)

        best_score = float("-inf")
        best_action = None

        for pawn in player.pawns:
            if not pawn.active:
                continue

            valid_moves = Movement.get_valid_moves_for_pawn(game, pawn)
            for row, col in valid_moves:
                score = self._evaluate_move(game, pawn, row, col, target_cells)
                if score > best_score:
                    best_score = score
                    best_action = (pawn, row, col)

        return best_action