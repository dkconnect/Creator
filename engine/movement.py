class Movement:
    DIRECTIONS = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    ]

    @staticmethod
    def get_valid_moves_for_pawn(game, pawn):
        if pawn is None:
            return []

        if not pawn.active:
            return []

        if game.dice.value is None:
            return []

        moves = []
        distance = game.dice.value

        for dr, dc in Movement.DIRECTIONS:
            row = pawn.row + dr * distance
            col = pawn.col + dc * distance

            # Outside the board.
            if not (0 <= row < game.board.size and 0 <= col < game.board.size):
                continue

            target = game.board.get_pawn(row, col)

            # Friendly pawn blocks the destination.
            if target is not None and target.team == pawn.team:
                continue

            # Empty or opponent pawn is legal.
            moves.append((row, col))

        return moves

    @staticmethod
    def get_valid_moves(game):
        if game.selected_pawn is None:
            return []

        return Movement.get_valid_moves_for_pawn(
            game,
            game.selected_pawn
        )

    @staticmethod
    def player_has_legal_move(game, player):
        for pawn in player.pawns:
            if not pawn.active:
                continue

            if Movement.get_valid_moves_for_pawn(game, pawn):
                return True

        return False