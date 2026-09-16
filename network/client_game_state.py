class ClientGameState:
    def __init__(self):
        self.board_size = 16

        self.current_player = None
        self.turn_phase = None
        self.dice = None

        self.selected_pawn_id = None

        self.game_over = False
        self.winner = None

        self.pattern = None
        self.players = None

    def update(self, state):
        """
        Replace local display state with an authoritative
        GAME_STATE received from the server.
        """

        if not isinstance(state, dict):
            return False

        required = (
            "board_size",
            "current_player",
            "turn_phase",
            "dice",
            "selected_pawn_id",
            "game_over",
            "winner",
            "pattern",
            "players",
        )

        if not all(
            key in state
            for key in required
        ):
            return False

        self.board_size = state["board_size"]

        self.current_player = state[
            "current_player"
        ]

        self.turn_phase = state[
            "turn_phase"
        ]

        self.dice = state["dice"]

        self.selected_pawn_id = state[
            "selected_pawn_id"
        ]

        self.game_over = state[
            "game_over"
        ]

        self.winner = state["winner"]

        self.pattern = state["pattern"]
        self.players = state["players"]

        return True