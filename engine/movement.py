class Movement:
    @staticmethod
    def get_valid_moves(game):
        if game.selected_pawn is None:
            return []

        moves = []

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]

        distance = game.dice.value
        pawn = game.selected_pawn

        for dr, dc in directions:
            row = pawn.row + dr * distance
            col = pawn.col + dc * distance

            if not (0 <= row < game.board.size and 0 <= col < game.board.size):
                continue

            target = game.board.get_pawn(row, col)

            if target is not None and target.team == pawn.team:
                continue

            moves.append((row, col))

        return moves
