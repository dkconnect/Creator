from engine.game import Game
from engine.protocol import Protocol
from network.server_handler import ServerHandler


def test_protocol_creates_roll_message():
    message = Protocol.roll()

    assert message == {
        "version": Protocol.VERSION,
        "type": Protocol.ROLL,
        "data": {},
    }

    assert Protocol.is_valid(message)


def test_blue_can_roll_during_blue_turn():
    game = Game()
    handler = ServerHandler(game)

    response = handler.handle_message(
        Protocol.roll(),
        client_team="BLUE"
    )

    assert response["type"] == Protocol.GAME_STATE
    assert game.dice.value is not None


def test_red_cannot_roll_during_blue_turn():
    game = Game()
    handler = ServerHandler(game)

    response = handler.handle_message(
        Protocol.roll(),
        client_team="RED"
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Not your turn"
    )

    assert game.dice.value is None


def test_client_cannot_roll_twice():
    game = Game()
    handler = ServerHandler(game)

    first_response = handler.handle_message(
        Protocol.roll(),
        client_team="BLUE"
    )

    assert first_response["type"] == Protocol.GAME_STATE

    # Normally a legal roll leaves the player waiting
    # to select a pawn. If the roll auto-skipped because
    # there were no legal moves, the turn has already changed.
    if game.current_player.team == "BLUE":
        second_response = handler.handle_message(
            Protocol.roll(),
            client_team="BLUE"
        )

        assert second_response["type"] == Protocol.ERROR
        assert second_response["data"]["message"] == (
            "Cannot roll now"
        )


def test_roll_rejects_missing_client_team():
    game = Game()
    handler = ServerHandler(game)

    response = handler.handle_message(
        Protocol.roll()
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Invalid client team"
    )


def test_roll_rejects_invalid_client_team():
    game = Game()
    handler = ServerHandler(game)

    response = handler.handle_message(
        Protocol.roll(),
        client_team="GREEN"
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Invalid client team"
    )


def test_roll_response_contains_authoritative_state():
    game = Game()
    handler = ServerHandler(game)

    response = handler.handle_message(
        Protocol.roll(),
        client_team="BLUE"
    )

    assert response == Protocol.game_state(
        game
    )