from engine.protocol import Protocol
from network.tcp_client import TcpGameClient
from network.client_game_state import ClientGameState


class MultiplayerClient:
    def __init__(
        self,
        host="127.0.0.1",
        port=5555
    ):
        self.client = TcpGameClient(
            host=host,
            port=port
        )

        self.room_code = None
        self.team = None

        self.game_state = ClientGameState()
        self.lobby_state = None
        self.reconnect_token = None
        self.room_status = None

    def connect(self):
        return self.client.connect()

    def disconnect(self):
        self.client.disconnect()

        self.room_code = None
        self.team = None
        self.lobby_state = None
        self.reconnect_token = None
        self.room_status = None

    def create_room(self):
        response = self.client.request(
            Protocol.create_room()
        )

        return self._handle_room_response(
            response
        )

    def join_room(self, room_code):
        response = self.client.request(
            Protocol.join_room(
                room_code
            )
        )

        return self._handle_room_response(
            response
        )

    def reconnect(self):
        if not self.room_code or not self.reconnect_token:
            return False
        if self.client.socket is not None:
            self.client.disconnect()
        if not self.client.connect():
            return False
        response = self.client.request(
            Protocol.rejoin_room(self.room_code, self.reconnect_token)
        )
        if not response or response.get("type") != Protocol.ROOM_JOINED:
            self.client.disconnect()
            return False
        self._handle_room_response(response)
        return True

    def get_lobby(self):
        response = self.client.request(Protocol.get_lobby())
        if response and response.get("type") == Protocol.LOBBY_STATE:
            self.lobby_state = response["data"]
        return response

    def set_ready(self, ready):
        response = self.client.request(Protocol.set_ready(ready))
        if response and response.get("type") == Protocol.LOBBY_STATE:
            self.lobby_state = response["data"]
        return response

    def get_state(self):
        response = self.client.request(
            Protocol.get_state()
        )

        self._handle_game_state(
            response
        )

        return response

    def roll(self):
        response = self.client.request(
            Protocol.roll()
        )

        self._handle_game_state(
            response
        )

        return response

    def move(self, pawn_id, row, col):
        response = self.client.request(
            Protocol.move(
                pawn_id=pawn_id,
                row=row,
                col=col
            )
        )

        self._handle_game_state(
            response
        )

        return response

    def _handle_room_response(
        self,
        response
    ):
        if response is None:
            return None

        if (
            response.get("type")
            != Protocol.ROOM_JOINED
        ):
            return response

        data = response["data"]

        self.room_code = data["room_code"]
        self.team = data["team"]
        self.reconnect_token = data.get("reconnect_token", self.reconnect_token)

        return response

    def _handle_game_state(
        self,
        response
    ):
        if response is None:
            return False

        if (
            response.get("type")
            != Protocol.GAME_STATE
        ):
            return False

        self.room_status = response.get("room_status", self.room_status)
        return self.game_state.update(
            response["data"]
        )