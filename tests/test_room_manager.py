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