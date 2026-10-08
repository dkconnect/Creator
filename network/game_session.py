import secrets

from engine.game import Game
from network.server_handler import ServerHandler


class GameSession:
    def __init__(self, game=None):
        self.game = game if game is not None else Game()
        self.handler = ServerHandler(self.game)

        self.blue_client = None
        self.red_client = None
        self.ready = {"BLUE": False, "RED": False}
        self.started = False
        self.reconnect_tokens = {}
        self.disconnected = set()

    def add_client(self, client_id):
        """
        Add a client to the session.

        If the client is already connected, return its
        existing team without assigning another slot.

        Returns:
            "BLUE" or "RED" on success.
            None if the room is full.
        """

        existing_team = self.get_client_team(
            client_id
        )

        if existing_team is not None:
            return existing_team

        if self.started:
            return None

        if self.blue_client is None:
            self.blue_client = client_id
            self.ready["BLUE"] = False
            self.reconnect_tokens["BLUE"] = secrets.token_urlsafe(32)
            return "BLUE"

        if self.red_client is None:
            self.red_client = client_id
            self.ready["RED"] = False
            self.reconnect_tokens["RED"] = secrets.token_urlsafe(32)
            return "RED"

        return None

    def remove_client(self, client_id):
        """
        Remove a client from the session.

        Returns the team that was released,
        or None if the client was not in the session.
        """

        if self.blue_client == client_id:
            if self.started:
                self.disconnected.add("BLUE")
                return "BLUE"
            self.reconnect_tokens.pop("BLUE", None)
            self.blue_client = None
            self.ready["BLUE"] = False
            self.reconnect_tokens["BLUE"] = secrets.token_urlsafe(32)
            return "BLUE"

        if self.red_client == client_id:
            if self.started:
                self.disconnected.add("RED")
                return "RED"
            self.reconnect_tokens.pop("RED", None)
            self.red_client = None
            self.ready["RED"] = False
            self.reconnect_tokens["RED"] = secrets.token_urlsafe(32)
            return "RED"

        return None

    def reconnect(self, client_id, token):
        if not self.started or not isinstance(token, str):
            return None
        for team in ("BLUE", "RED"):
            if (team in self.disconnected
                    and secrets.compare_digest(self.reconnect_tokens.get(team, ""), token)):
                if team == "BLUE":
                    self.blue_client = client_id
                else:
                    self.red_client = client_id
                self.disconnected.remove(team)
                return team
        return None

    @property
    def paused(self):
        return self.started and bool(self.disconnected)

    def get_client_team(self, client_id):
        if self.blue_client == client_id:
            return "BLUE"

        if self.red_client == client_id:
            return "RED"

        return None

    def is_full(self):
        return (
            self.blue_client is not None
            and self.red_client is not None
        )

    def lobby_state(self):
        return {
            "players": {
                "BLUE": {"connected": self.blue_client is not None and "BLUE" not in self.disconnected, "ready": self.ready["BLUE"]},
                "RED": {"connected": self.red_client is not None and "RED" not in self.disconnected, "ready": self.ready["RED"]},
            },
            "started": self.started,
            "paused": self.paused,
        }

    def handle_client_message(self, client_id, message):
        """
        Route a client message through the authoritative
        server handler using the client's assigned team.
        """

        team = self.get_client_team(client_id)

        from engine.protocol import Protocol
        kind = message.get("type")
        if team is None:
            return Protocol.error("Invalid client team")
        if kind == Protocol.GET_LOBBY:
            return Protocol.lobby_state(self.lobby_state())
        if kind == Protocol.SET_READY:
            ready = message.get("data", {}).get("ready")
            if type(ready) is not bool:
                return Protocol.error("Ready must be a boolean")
            if self.started:
                return Protocol.error("Match already started")
            self.ready[team] = ready
            if self.is_full() and all(self.ready.values()):
                self.started = True
            return Protocol.lobby_state(self.lobby_state())
        if kind in (Protocol.ROLL, Protocol.MOVE) and self.paused:
            return Protocol.error("Match paused: waiting for player to reconnect")
        if kind in (Protocol.ROLL, Protocol.MOVE) and not self.started:
            return Protocol.error("Match has not started")
        response = self.handler.handle_message(
            message,
            client_team=team
        )
        if response.get("type") == Protocol.GAME_STATE:
            response["room_status"] = self.lobby_state()
        return response