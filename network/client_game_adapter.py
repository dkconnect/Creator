from types import SimpleNamespace

from engine.movement import Movement


class ClientBoard:
    def __init__(self, size):
        self.size = size
        self.grid = [
            [None for _ in range(size)]
            for _ in range(size)
        ]

    def get_pawn(self, row, col):
        return self.grid[row][col]


class ClientGameAdapter:
    """
    Display-only view of an authoritative multiplayer snapshot.
    """

    def __init__(self, client_state):
        self.client_state = client_state

        self.board = ClientBoard(
            client_state.board_size
        )

        self.blue = SimpleNamespace(
            team="BLUE",
            pawns=[],
            respawns=0,
            reserve=[]
        )

        self.red = SimpleNamespace(
            team="RED",
            pawns=[],
            respawns=0,
            reserve=[]
        )

        self.pattern = SimpleNamespace(
            name=None,
            size=0,
            grid=[]
        )

        self.dice = SimpleNamespace(
            value=None
        )

        self.current_player = None
        self.selected_pawn = None
        self.game_over = False
        self.winner = None

        self.refresh()

    def refresh(self):
        state = self.client_state

        self.board = ClientBoard(
            state.board_size
        )

        self.dice.value = state.dice
        self.game_over = state.game_over

        pattern = state.pattern or {}

        self.pattern.name = pattern.get(
            "name"
        )

        self.pattern.size = pattern.get(
            "size",
            0
        )

        self.pattern.grid = pattern.get(
            "grid",
            []
        )

        for team, player in (
            ("BLUE", self.blue),
            ("RED", self.red)
        ):
            data = (
                state.players or {}
            ).get(team, {})

            player.respawns = data.get(
                "respawns",
                0
            )

            player.captures_suffered = data.get(
                "captures_suffered",
                0
            )

            player.pawns = [
                SimpleNamespace(**pawn)
                for pawn in data.get(
                    "pawns",
                    []
                )
            ]

            reserve_ids = set(
                data.get(
                    "reserve",
                    []
                )
            )

            player.reserve = [
                pawn
                for pawn in player.pawns
                if pawn.id in reserve_ids
            ]

            for pawn in player.pawns:

                if not pawn.active:
                    continue

                if not (
                    0 <= pawn.row < self.board.size
                    and 0 <= pawn.col < self.board.size
                ):
                    continue

                self.board.grid[
                    pawn.row
                ][pawn.col] = pawn

        teams = {
            "BLUE": self.blue,
            "RED": self.red
        }

        self.current_player = teams.get(
            state.current_player
        )

        self.winner = teams.get(
            state.winner
        )

        self.selected_pawn = None

        if state.selected_pawn_id is not None:

            for player in (
                self.blue,
                self.red
            ):
                for pawn in player.pawns:

                    if pawn.id == state.selected_pawn_id:
                        self.selected_pawn = pawn
                        break

                if self.selected_pawn is not None:
                    break

    def get_valid_moves(self):
        if (
            self.game_over
            or self.selected_pawn is None
            or self.dice.value is None
        ):
            return []

        return Movement.get_valid_moves_for_pawn(
            self,
            self.selected_pawn
        )