class Capture:

    @staticmethod
    def handle_capture(game, captured_pawn):
        if captured_pawn is None:
            return

        if (
            0 <= captured_pawn.row < game.board.size
            and 0 <= captured_pawn.col < game.board.size
            and game.board.get_pawn(
                captured_pawn.row,
                captured_pawn.col
            ) is captured_pawn
        ):
            game.board.grid[captured_pawn.row][captured_pawn.col] = None

        captured_pawn.active = False
        game.respawn_pawn(captured_pawn)