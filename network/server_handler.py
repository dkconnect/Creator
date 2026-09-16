from engine.protocol import Protocol


class ServerHandler:
    def __init__(self, game):
        self.game = game

    def handle_message(self, message):
        """
        Process one client protocol message.

        Returns a protocol response dictionary.
        """

        if not Protocol.is_valid(message):
            return Protocol.error(
                "Invalid protocol message"
            )

        if message["type"] == Protocol.MOVE:
            return self._handle_move(
                message["data"]
            )

        return Protocol.error(
            "Message type not accepted from client"
        )

    def _handle_move(self, data):
        required_fields = (
            "pawn_id",
            "row",
            "col",
        )

        if not all(
            field in data
            for field in required_fields
        ):
            return Protocol.error(
                "Invalid move data"
            )

        success = self.game.submit_move(
            pawn_id=data["pawn_id"],
            row=data["row"],
            col=data["col"],
        )

        if not success:
            return Protocol.error(
                "Illegal move"
            )

        return Protocol.game_state(
            self.game
        )