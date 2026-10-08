from network.room_manager import RoomManager


def test_create_room_returns_six_character_code():
    manager = RoomManager()

    room_code, team = manager.create_room(
        "client-a"
    )

    assert len(room_code) == 6
    assert room_code.isalnum()
    assert room_code == room_code.upper()
    assert team == "BLUE"


def test_created_room_can_be_retrieved():
    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    session = manager.get_room(
        room_code
    )

    assert session is not None
    assert session.blue_client == "client-a"


def test_second_client_joins_as_red():
    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    team = manager.join_room(
        room_code,
        "client-b"
    )

    assert team == "RED"

    session = manager.get_room(
        room_code
    )

    assert session.red_client == "client-b"


def test_room_code_is_case_insensitive():
    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    team = manager.join_room(
        room_code.lower(),
        "client-b"
    )

    assert team == "RED"


def test_unknown_room_cannot_be_joined():
    manager = RoomManager()

    team = manager.join_room(
        "ABC123",
        "client-a"
    )

    assert team is None


def test_third_client_cannot_join_full_room():
    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    manager.join_room(
        room_code,
        "client-b"
    )

    team = manager.join_room(
        room_code,
        "client-c"
    )

    assert team is None


def test_remove_client_from_room():
    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    manager.join_room(
        room_code,
        "client-b"
    )

    released_team = manager.remove_client(
        room_code,
        "client-b"
    )

    assert released_team == "RED"

    session = manager.get_room(
        room_code
    )

    assert session.red_client is None


def test_delete_room():
    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    assert manager.delete_room(
        room_code
    )

    assert manager.get_room(
        room_code
    ) is None


def test_delete_unknown_room_returns_false():
    manager = RoomManager()

    assert not manager.delete_room(
        "ABC123"
    )


def test_different_rooms_have_different_codes():
    manager = RoomManager()

    first_code, _ = manager.create_room(
        "client-a"
    )

    second_code, _ = manager.create_room(
        "client-b"
    )

    assert first_code != second_code

def test_creator_rejoining_keeps_blue_team():
    manager = RoomManager()

    room_code, team = manager.create_room(
        "client-a"
    )

    assert team == "BLUE"

    rejoined_team = manager.join_room(
        room_code,
        "client-a"
    )

    assert rejoined_team == "BLUE"

    session = manager.get_room(
        room_code
    )

    assert session.blue_client == "client-a"
    assert session.red_client is None


def test_red_client_rejoining_keeps_red_team():
    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    manager.join_room(
        room_code,
        "client-b"
    )

    rejoined_team = manager.join_room(
        room_code,
        "client-b"
    )

    assert rejoined_team == "RED"

    session = manager.get_room(
        room_code
    )

    assert session.blue_client == "client-a"
    assert session.red_client == "client-b"


def test_duplicate_creator_join_does_not_fill_room():
    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    manager.join_room(
        room_code,
        "client-a"
    )

    session = manager.get_room(
        room_code
    )

    assert not session.is_full()


def test_unique_second_client_can_join_after_creator_rejoins():
    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    manager.join_room(
        room_code,
        "client-a"
    )

    team = manager.join_room(
        room_code,
        "client-b"
    )

    assert team == "RED"

    session = manager.get_room(
        room_code
    )

    assert session.is_full()

def test_room_manager_routes_blue_roll():
    from engine.protocol import Protocol

    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    manager.join_room(
        room_code,
        "client-b"
    )

    manager.handle_client_message(room_code, "client-a", Protocol.set_ready(True))
    manager.handle_client_message(room_code, "client-b", Protocol.set_ready(True))

    response = manager.handle_client_message(
        room_code,
        "client-a",
        Protocol.roll()
    )

    assert response["type"] == Protocol.GAME_STATE

    session = manager.get_room(
        room_code
    )

    assert session.game.dice.value is not None


def test_room_manager_blocks_red_roll_on_blue_turn():
    from engine.protocol import Protocol

    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    manager.join_room(
        room_code,
        "client-b"
    )

    manager.handle_client_message(room_code, "client-a", Protocol.set_ready(True))
    manager.handle_client_message(room_code, "client-b", Protocol.set_ready(True))

    response = manager.handle_client_message(
        room_code,
        "client-b",
        Protocol.roll()
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Not your turn"
    )


def test_room_manager_blocks_unknown_client():
    from engine.protocol import Protocol

    manager = RoomManager()

    room_code, _ = manager.create_room(
        "client-a"
    )

    response = manager.handle_client_message(
        room_code,
        "intruder",
        Protocol.roll()
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Invalid client team"
    )


def test_room_manager_unknown_room_returns_none():
    from engine.protocol import Protocol

    manager = RoomManager()

    response = manager.handle_client_message(
        "ABC123",
        "client-a",
        Protocol.roll()
    )

    assert response is None