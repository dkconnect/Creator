from engine.protocol import Protocol
from network.game_session import GameSession


def test_first_client_becomes_blue():
    session = GameSession()

    team = session.add_client(
        "client-a"
    )

    assert team == "BLUE"
    assert session.blue_client == "client-a"


def test_second_client_becomes_red():
    session = GameSession()

    session.add_client("client-a")

    team = session.add_client(
        "client-b"
    )

    assert team == "RED"
    assert session.red_client == "client-b"


def test_third_client_is_rejected():
    session = GameSession()

    session.add_client("client-a")
    session.add_client("client-b")

    team = session.add_client(
        "client-c"
    )

    assert team is None


def test_session_reports_when_full():
    session = GameSession()

    assert not session.is_full()

    session.add_client("client-a")

    assert not session.is_full()

    session.add_client("client-b")

    assert session.is_full()


def test_get_client_team():
    session = GameSession()

    session.add_client("client-a")
    session.add_client("client-b")

    assert (
        session.get_client_team("client-a")
        == "BLUE"
    )

    assert (
        session.get_client_team("client-b")
        == "RED"
    )

    assert (
        session.get_client_team("unknown")
        is None
    )


def test_remove_client_releases_team():
    session = GameSession()

    session.add_client("client-a")
    session.add_client("client-b")

    team = session.remove_client(
        "client-a"
    )

    assert team == "BLUE"
    assert session.blue_client is None
    assert not session.is_full()


def test_new_client_can_take_released_team():
    session = GameSession()

    session.add_client("client-a")
    session.add_client("client-b")

    session.remove_client("client-a")

    team = session.add_client(
        "client-c"
    )

    assert team == "BLUE"
    assert session.blue_client == "client-c"


def test_unknown_client_cannot_act():
    session = GameSession()

    session.add_client("client-a")
    session.add_client("client-b")

    response = session.handle_client_message(
        "intruder",
        Protocol.roll()
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Invalid client team"
    )


def test_blue_client_can_roll_on_blue_turn():
    session = GameSession()

    session.add_client("client-a")
    session.add_client("client-b")

    response = session.handle_client_message(
        "client-a",
        Protocol.roll()
    )

    assert response["type"] == Protocol.GAME_STATE
    assert session.game.dice.value is not None


def test_red_client_cannot_roll_on_blue_turn():
    session = GameSession()

    session.add_client("client-a")
    session.add_client("client-b")

    response = session.handle_client_message(
        "client-b",
        Protocol.roll()
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Not your turn"
    )

def test_same_client_cannot_take_both_teams():
    session = GameSession()

    first_team = session.add_client(
        "client-a"
    )

    second_team = session.add_client(
        "client-a"
    )

    assert first_team == "BLUE"
    assert second_team == "BLUE"

    assert session.blue_client == "client-a"
    assert session.red_client is None


def test_rejoining_red_client_keeps_red_team():
    session = GameSession()

    session.add_client("client-a")
    session.add_client("client-b")

    team = session.add_client(
        "client-b"
    )

    assert team == "RED"
    assert session.blue_client == "client-a"
    assert session.red_client == "client-b"


def test_duplicate_join_does_not_make_session_full():
    session = GameSession()

    session.add_client("client-a")
    session.add_client("client-a")

    assert not session.is_full()


def test_second_unique_client_can_join_after_duplicate():
    session = GameSession()

    session.add_client("client-a")
    session.add_client("client-a")

    team = session.add_client(
        "client-b"
    )

    assert team == "RED"
    assert session.is_full()