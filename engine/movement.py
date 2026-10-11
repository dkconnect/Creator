class Movement:
    """Eight-direction movement: choose 1..die.value squares per turn.

    Pieces may jump over occupied intermediate squares (existing rule).
    A friendly piece blocks only the landing square; an enemy can be captured.
    """

    DIRECTIONS = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1),
    ]

    @staticmethod
    def get_valid_moves_for_pawn(game, pawn):
        if pawn is None or not pawn.active or game.dice.value is None:
            return []
        moves = []
        for distance in range(1, max(0, int(game.dice.value)) + 1):
            for dr, dc in Movement.DIRECTIONS:
                row = pawn.row + dr * distance
                col = pawn.col + dc * distance
                if not (0 <= row < game.board.size and 0 <= col < game.board.size):
                    continue
                target = game.board.get_pawn(row, col)
                if target is not None and target.team == pawn.team:
                    continue
                moves.append((row, col))
        return moves

    @staticmethod
    def get_valid_moves(game):
        if game.selected_pawn is None:
            return []
        return Movement.get_valid_moves_for_pawn(game, game.selected_pawn)

    @staticmethod
    def player_has_legal_move(game, player):
        return any(pawn.active and Movement.get_valid_moves_for_pawn(game, pawn)
                   for pawn in player.pawns)
