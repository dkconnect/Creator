class Capture:
    @staticmethod
    def handle_capture(game, captured_pawn):
        if captured_pawn is not None:
            game.respawn_pawn(captured_pawn)
