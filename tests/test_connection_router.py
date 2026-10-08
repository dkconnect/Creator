from engine.protocol import Protocol
from network.connection_router import ConnectionRouter


def test_client_can_create_room():
    router = ConnectionRouter()

    response = router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    assert response["type"] == Protocol.ROOM_JOINED
    assert response["data"]["team"] == "BLUE"

    room_code = response["data"]["room_code"]

    assert len(room_code) == 6
    assert router.client_rooms["client-a"] == room_code


def test_second_client_can_join_room():
    router = ConnectionRouter()

    create_response = router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    room_code = create_response["data"]["room_code"]

    join_response = router.handle_message(
        "client-b",
        Protocol.join_room(room_code)
    )

    assert join_response["type"] == Protocol.ROOM_JOINED
    assert join_response["data"]["room_code"] == room_code
    assert join_response["data"]["team"] == "RED"

    assert router.client_rooms["client-b"] == room_code


def test_join_room_is_case_insensitive():
    router = ConnectionRouter()

    create_response = router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    room_code = create_response["data"]["room_code"]

    response = router.handle_message(
        "client-b",
        Protocol.join_room(
            room_code.lower()
        )
    )

    assert response["type"] == Protocol.ROOM_JOINED
    assert response["data"]["team"] == "RED"


def test_unknown_room_is_rejected():
    router = ConnectionRouter()

    response = router.handle_message(
        "client-a",
        Protocol.join_room("ABC123")
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Unable to join room"
    )


def test_third_client_cannot_join_full_room():
    router = ConnectionRouter()

    create_response = router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    room_code = create_response["data"]["room_code"]

    router.handle_message(
        "client-b",
        Protocol.join_room(room_code)
    )

    response = router.handle_message(
        "client-c",
        Protocol.join_room(room_code)
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Unable to join room"
    )


def test_client_cannot_create_second_room():
    router = ConnectionRouter()

    router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    response = router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Client is already in a room"
    )


def test_client_cannot_join_another_room():
    router = ConnectionRouter()

    first = router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    first_code = first["data"]["room_code"]

    second = router.handle_message(
        "client-b",
        Protocol.create_room()
    )

    second_code = second["data"]["room_code"]

    response = router.handle_message(
        "client-a",
        Protocol.join_room(second_code)
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Client is already in a room"
    )

    assert router.client_rooms["client-a"] == first_code


def test_client_must_join_room_before_gameplay():
    router = ConnectionRouter()

    response = router.handle_message(
        "client-a",
        Protocol.roll()
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Client is not in a room"
    )


def test_blue_roll_routes_into_correct_session():
    router = ConnectionRouter()

    create_response = router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    room_code = create_response["data"]["room_code"]

    router.handle_message(
        "client-b",
        Protocol.join_room(room_code)
    )

    router.handle_message("client-a", Protocol.set_ready(True))
    router.handle_message("client-b", Protocol.set_ready(True))

    response = router.handle_message(
        "client-a",
        Protocol.roll()
    )

    assert response["type"] == Protocol.GAME_STATE

    session = router.room_manager.get_room(
        room_code
    )

    assert session.game.dice.value is not None


def test_red_cannot_roll_on_blue_turn():
    router = ConnectionRouter()

    create_response = router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    room_code = create_response["data"]["room_code"]

    router.handle_message(
        "client-b",
        Protocol.join_room(room_code)
    )

    router.handle_message("client-a", Protocol.set_ready(True))
    router.handle_message("client-b", Protocol.set_ready(True))

    response = router.handle_message(
        "client-b",
        Protocol.roll()
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Not your turn"
    )

def test_remove_blue_client_from_room():
    router = ConnectionRouter()

    response = router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    room_code = response["data"]["room_code"]

    team = router.remove_client(
        "client-a"
    )

    assert team == "BLUE"

    assert "client-a" not in (
        router.client_rooms
    )

    session = router.room_manager.get_room(
        room_code
    )

    assert session.blue_client is None


def test_remove_red_client_from_room():
    router = ConnectionRouter()

    response = router.handle_message(
        "client-a",
        Protocol.create_room()
    )

    room_code = response["data"]["room_code"]

    router.handle_message(
        "client-b",
        Protocol.join_room(room_code)
    )

    team = router.remove_client(
        "client-b"
    )

    assert team == "RED"

    assert "client-b" not in (
        router.client_rooms
    )

    session = router.room_manager.get_room(
        room_code
    )

    assert session.red_client is None


def test_remove_unknown_client_returns_none():
    router = ConnectionRouter()

    assert router.remove_client(
        "unknown-client"
    ) is None