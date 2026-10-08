from engine.game import Game
from engine.protocol import Protocol
from network.server_handler import ServerHandler


def test_get_state_protocol():
    message = Protocol.get_state()

    assert Protocol.is_valid(message)
    assert message["type"] == Protocol.GET_STATE
    assert message["data"] == {}


def test_get_state_returns_game_state():
    game = Game()
    handler = ServerHandler(game)

    response = handler.handle_message(
        Protocol.get_state(),
        client_team="BLUE"
    )

    assert response["type"] == Protocol.GAME_STATE
    assert response["data"] == game.to_dict()


def test_get_state_allowed_for_red():
    handler = ServerHandler(Game())

    response = handler.handle_message(
        Protocol.get_state(),
        client_team="RED"
    )

    assert response["type"] == Protocol.GAME_STATE


def test_get_state_rejects_unknown_client():
    handler = ServerHandler(Game())

    response = handler.handle_message(
        Protocol.get_state(),
        client_team=None
    )

    assert response["type"] == Protocol.ERROR


def test_get_state_does_not_change_game():
    game = Game()
    handler = ServerHandler(game)

    before = game.to_dict()

    handler.handle_message(
        Protocol.get_state(),
        client_team="BLUE"
    )

    assert game.to_dict() == before
    