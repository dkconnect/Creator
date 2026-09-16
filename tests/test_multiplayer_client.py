from engine.protocol import Protocol
from network.multiplayer_client import MultiplayerClient


class FakeTcpClient:
    def __init__(self):
        self.connected = False
        self.responses = []
        self.requests = []

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False

    def request(self, message):
        self.requests.append(
            message
        )

        if not self.responses:
            return None

        return self.responses.pop(0)


def make_multiplayer_client():
    multiplayer = MultiplayerClient()

    fake = FakeTcpClient()

    multiplayer.client = fake

    return multiplayer, fake


def test_connect_uses_tcp_client():
    multiplayer, fake = (
        make_multiplayer_client()
    )

    assert multiplayer.connect()
    assert fake.connected


def test_create_room_stores_room_and_team():
    multiplayer, fake = (
        make_multiplayer_client()
    )

    fake.responses.append(
        Protocol.room_joined(
            "ABC123",
            "BLUE"
        )
    )

    response = multiplayer.create_room()

    assert response["type"] == (
        Protocol.ROOM_JOINED
    )

    assert multiplayer.room_code == "ABC123"
    assert multiplayer.team == "BLUE"

    assert fake.requests == [
        Protocol.create_room()
    ]


def test_join_room_stores_room_and_team():
    multiplayer, fake = (
        make_multiplayer_client()
    )

    fake.responses.append(
        Protocol.room_joined(
            "ABC123",
            "RED"
        )
    )

    multiplayer.join_room(
        "ABC123"
    )

    assert multiplayer.room_code == "ABC123"
    assert multiplayer.team == "RED"

    assert fake.requests == [
        Protocol.join_room(
            "ABC123"
        )
    ]


def test_error_does_not_set_room():
    multiplayer, fake = (
        make_multiplayer_client()
    )

    fake.responses.append(
        Protocol.error(
            "Unable to join room"
        )
    )

    response = multiplayer.join_room(
        "ABC123"
    )

    assert response["type"] == Protocol.ERROR
    assert multiplayer.room_code is None
    assert multiplayer.team is None


def test_roll_sends_roll_message():
    multiplayer, fake = (
        make_multiplayer_client()
    )

    fake.responses.append(
        Protocol.error(
            "Test"
        )
    )

    multiplayer.roll()

    assert fake.requests == [
        Protocol.roll()
    ]


def test_move_sends_move_message():
    multiplayer, fake = (
        make_multiplayer_client()
    )

    fake.responses.append(
        Protocol.error(
            "Test"
        )
    )

    multiplayer.move(
        pawn_id=12,
        row=6,
        col=7
    )

    assert fake.requests == [
        Protocol.move(
            pawn_id=12,
            row=6,
            col=7
        )
    ]


def test_disconnect_clears_multiplayer_state():
    multiplayer, fake = (
        make_multiplayer_client()
    )

    multiplayer.room_code = "ABC123"
    multiplayer.team = "BLUE"

    multiplayer.disconnect()

    assert not fake.connected
    assert multiplayer.room_code is None
    assert multiplayer.team is None