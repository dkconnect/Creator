from engine.protocol import Protocol


class ServerHandler:
    def __init__(self, game):
        self.game = game

    def handle_message(self, message, client_team=None):
        """
        Process one client protocol message.

        client_team identifies which team the sending
        client controls.

        Returns a protocol response dictionary.
        """

        if not Protocol.is_valid(message):
            return Protocol.error(
                "Invalid protocol message"
            )

        # -------------------------
        # Roll
        # -------------------------

        if message["type"] == Protocol.ROLL:
            return self._handle_roll(
                client_team
            )

        # -------------------------
        # Move
        # -------------------------

        if message["type"] == Protocol.MOVE:
            return self._handle_move(
                message["data"],
                client_team
            )

        # GAME_STATE and ERROR are server-side messages.
        return Protocol.error(
            "Message type not accepted from client"
        )

    def _handle_roll(self, client_team):
        """
        Handle a dice-roll request from a client.
        """

        if client_team not in ("BLUE", "RED"):
            return Protocol.error(
                "Invalid client team"
            )

        if self.game.current_player.team != client_team:
            return Protocol.error(
                "Not your turn"
            )

        if (
            self.game.turn_phase
            != self.game.WAITING_FOR_ROLL
        ):
            return Protocol.error(
                "Cannot roll now"
            )

        self.game.roll_dice()

        return Protocol.game_state(
            self.game
        )

    def _handle_move(self, data, client_team):
        """
        Handle a move request from a client.
        """

        if client_team not in ("BLUE", "RED"):
            return Protocol.error(
                "Invalid client team"
            )

        if self.game.current_player.team != client_team:
            return Protocol.error(
                "Not your turn"
            )

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