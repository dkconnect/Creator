import json

from engine.game import Game
from engine.protocol import Protocol


def test_move_message():
    message = Protocol.move(
        pawn_id=16,
        row=5,
        col=8
    )

    assert message == {
        "version": 1,
        "type": "MOVE",
        "data": {
            "pawn_id": 16,
            "row": 5,
            "col": 8,
        },
    }


def test_game_state_message():
    game = Game()

    message = Protocol.game_state(game)

    assert message["version"] == Protocol.VERSION
    assert message["type"] == Protocol.GAME_STATE
    assert message["data"] == game.to_dict()


def test_error_message():
    message = Protocol.error(
        "Illegal move"
    )

    assert message == {
        "version": 1,
        "type": "ERROR",
        "data": {
            "message": "Illegal move",
        },
    }


def test_protocol_messages_are_json_serializable():
    game = Game()

    messages = [
        Protocol.move(16, 5, 8),
        Protocol.game_state(game),
        Protocol.error("Test error"),
    ]

    for message in messages:
        encoded = json.dumps(message)

        assert isinstance(encoded, str)


def test_valid_move_message():
    message = Protocol.move(
        16,
        5,
        8
    )

    assert Protocol.is_valid(message)


def test_rejects_wrong_protocol_version():
    message = Protocol.move(
        16,
        5,
        8
    )

    message["version"] = 999

    assert not Protocol.is_valid(message)


def test_rejects_unknown_message_type():
    message = {
        "version": Protocol.VERSION,
        "type": "HACK_THE_PLANET",
        "data": {},
    }

    assert not Protocol.is_valid(message)


def test_rejects_non_dictionary_message():
    assert not Protocol.is_valid(
        "MOVE"
    )


def test_rejects_missing_data():
    message = {
        "version": Protocol.VERSION,
        "type": Protocol.MOVE,
    }

    assert not Protocol.is_valid(message)