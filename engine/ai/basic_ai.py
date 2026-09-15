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

        # High priority: Land directly on a required pattern square
        if (target_row, target_col) in target_cells:
            score += 100.0

        # Medium priority: Capture opponent piece
        target_pawn = game.board.get_pawn(target_row, target_col)
        if target_pawn is not None and target_pawn.team != self.team:
            score += 40.0

        # Proximity: Move closer to nearest empty/opponent-held pattern cell
        unfilled_targets = [
            (tr, tc) for tr, tc in target_cells
            if game.board.get_pawn(tr, tc) is None or game.board.get_pawn(tr, tc).team != self.team
        ]

        if unfilled_targets:
            min_dist = min(
                abs(target_row - tr) + abs(target_col - tc)
                for tr, tc in unfilled_targets
            )
            score -= min_dist * 2.0

        score += random.uniform(0.0, 1.0)
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