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
        self.rematch = {"BLUE": False, "RED": False}
        self.match_number = 1
        self.event_id = 0
        self.last_event = None
        self.move_history = []

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
            "rematch": dict(self.rematch),
            "match_number": self.match_number,
            "event_id": self.event_id,
            "last_event": self.last_event,
            "move_history": [dict(event) for event in self.move_history],
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
        if kind == Protocol.SET_REMATCH:
            if not self.started or not self.game.game_over:
                return Protocol.error("Rematch is available only after the match ends")
            if self.paused:
                return Protocol.error("Match paused: waiting for player to reconnect")
            ready = message.get("data", {}).get("ready")
            if type(ready) is not bool:
                return Protocol.error("Rematch vote must be a boolean")
            self.rematch[team] = ready
            if all(self.rematch.values()):
                self.game = Game()
                self.handler = ServerHandler(self.game)
                self.rematch = {"BLUE": False, "RED": False}
                self.match_number += 1
                self.event_id = 0
                self.last_event = None
                self.move_history = []
            return Protocol.lobby_state(self.lobby_state())
        if kind in (Protocol.ROLL, Protocol.MOVE) and self.paused:
            return Protocol.error("Match paused: waiting for player to reconnect")
        if kind in (Protocol.ROLL, Protocol.MOVE) and not self.started:
            return Protocol.error("Match has not started")
        before = None
        if kind == Protocol.MOVE:
            before = {p.id: (p.row, p.col, p.active)
                      for player in (self.game.blue, self.game.red)
                      for p in player.pawns}
        response = self.handler.handle_message(
            message,
            client_team=team
        )
        if response.get("type") == Protocol.GAME_STATE and kind in (Protocol.ROLL, Protocol.MOVE):
            self.event_id += 1
            if kind == Protocol.ROLL:
                self.last_event = {"type": "ROLL", "team": team,
                                   "value": self.game.dice.value, "id": self.event_id}
            else:
                data = message["data"]
                victims = [p for player in (self.game.blue, self.game.red)
                           if player.team != team for p in player.pawns
                           if before[p.id] != (p.row, p.col, p.active)]
                self.last_event = {"type": "MOVE", "team": team,
                                   "pawn_id": data["pawn_id"],
                                   "row": data["row"], "col": data["col"],
                                   "captures": len(victims), "id": self.event_id}
        if self.last_event is not None and self.last_event.get("id") == self.event_id and kind in (Protocol.ROLL, Protocol.MOVE) and response.get("type") == Protocol.GAME_STATE:
            self.move_history.append(dict(self.last_event))
            self.move_history = self.move_history[-12:]
        if response.get("type") == Protocol.GAME_STATE:
            response["room_status"] = self.lobby_state()
        return response