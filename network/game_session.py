from engine.game import Game
from network.server_handler import ServerHandler


class GameSession:
    def __init__(self, game=None):
        self.game = game if game is not None else Game()
        self.handler = ServerHandler(self.game)

        self.blue_client = None
        self.red_client = None

    def add_client(self, client_id):
        """
        Add a client to the first available team.

        Returns:
            "BLUE" or "RED" on success.
            None if the room is full.
        """

        if self.blue_client is None:
            self.blue_client = client_id
            return "BLUE"

        if self.red_client is None:
            self.red_client = client_id
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
            return "BLUE"

        if self.red_client == client_id:
            self.red_client = None
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

    def handle_client_message(self, client_id, message):
        """
        Route a client message through the authoritative
        server handler using the client's assigned team.
        """

        team = self.get_client_team(client_id)

        return self.handler.handle_message(
            message,
            client_team=team
        )from engine.game import Game
from network.server_handler import ServerHandler


class GameSession:
    def __init__(self, game=None):
        self.game = game if game is not None else Game()
        self.handler = ServerHandler(self.game)

        self.blue_client = None
        self.red_client = None

    def add_client(self, client_id):
        """
        Add a client to the first available team.

        Returns:
            "BLUE" or "RED" on success.
            None if the room is full.
        """

        if self.blue_client is None:
            self.blue_client = client_id
            return "BLUE"

        if self.red_client is None:
            self.red_client = client_id
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
            return "BLUE"

        if self.red_client == client_id:
            self.red_client = None
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

    def handle_client_message(self, client_id, message):
        """
        Route a client message through the authoritative
        server handler using the client's assigned team.
        """

        team = self.get_client_team(client_id)

        return self.handler.handle_message(
            message,
            client_team=team
        )