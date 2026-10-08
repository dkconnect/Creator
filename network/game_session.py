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
            return "BLUE"

        if self.red_client is None:
            self.red_client = client_id
            self.ready["RED"] = False
            return "RED"

        return None

    def remove_client(self, client_id):
        """
        Remove a client from the session.

        Returns the team that was released,
        or None if the client was not in the session.
        """

        if self.blue_client == client_id:
            self.blue_client = None
            self.ready["BLUE"] = False
            return "BLUE"

        if self.red_client == client_id:
            self.red_client = None
            self.ready["RED"] = False
            return "RED"

        return None

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
                "BLUE": {"connected": self.blue_client is not None, "ready": self.ready["BLUE"]},
                "RED": {"connected": self.red_client is not None, "ready": self.ready["RED"]},
            },
            "started": self.started,
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
        if kind in (Protocol.ROLL, Protocol.MOVE) and not self.started:
            return Protocol.error("Match has not started")
        return self.handler.handle_message(
            message,
            client_team=team
        )