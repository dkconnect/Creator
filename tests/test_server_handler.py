from engine.game import Game
from engine.movement import Movement
from engine.protocol import Protocol
from network.server_handler import ServerHandler


def prepare_game():
    game = Game()

    game.dice.value = 1
    game.turn_phase = Game.WAITING_FOR_SELECTION

    return game


def find_legal_move(game):
    for pawn in game.current_player.pawns:
        moves = Movement.get_valid_moves_for_pawn(
            game,
            pawn
        )

        if moves:
            row, col = moves[0]
            return pawn, row, col

    raise AssertionError(
        "Expected at least one legal move"
    )


def test_handler_rejects_invalid_protocol_message():
    game = prepare_game()
    handler = ServerHandler(game)

    response = handler.handle_message(
        {"bad": "message"}
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Invalid protocol message"
    )


def test_handler_rejects_server_only_message():
    game = prepare_game()
    handler = ServerHandler(game)

    message = Protocol.game_state(game)

    response = handler.handle_message(
        message
    )

    assert response["type"] == Protocol.ERROR


def test_handler_rejects_move_with_missing_data():
    game = prepare_game()
    handler = ServerHandler(game)

    message = {
        "version": Protocol.VERSION,
        "type": Protocol.MOVE,
        "data": {
            "pawn_id": 16,
        },
    }

    response = handler.handle_message(
        message
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Invalid move data"
    )


def test_handler_rejects_illegal_move():
    game = prepare_game()
    handler = ServerHandler(game)

    pawn, _, _ = find_legal_move(game)

    message = Protocol.move(
        pawn.id,
        15,
        15
    )

    response = handler.handle_message(
        message
    )

    assert response["type"] == Protocol.ERROR
    assert response["data"]["message"] == (
        "Illegal move"
    )


def test_handler_executes_legal_move():
    game = prepare_game()
    handler = ServerHandler(game)

    pawn, row, col = find_legal_move(game)

    message = Protocol.move(
        pawn.id,
        row,
        col
    )

    response = handler.handle_message(
        message
    )

    assert response["type"] == Protocol.GAME_STATE
    assert game.board.get_pawn(
        row,
        col
    ) is pawn


def test_handler_returns_updated_game_state():
    game = prepare_game()
    handler = ServerHandler(game)

    pawn, row, col = find_legal_move(game)

    message = Protocol.move(
        pawn.id,
        row,
        col
    )

    response = handler.handle_message(
        message
    )

    assert response == Protocol.game_state(
        game
    )


def test_illegal_message_does_not_change_board():
    game = prepare_game()
    handler = ServerHandler(game)

    original_positions = [
        (p.id, p.row, p.col, p.active)
        for p in game.blue.pawns + game.red.pawns
    ]

    message = Protocol.move(
        9999,
        15,
        15
    )

    response = handler.handle_message(
        message
    )

    assert response["type"] == Protocol.ERROR

    new_positions = [
        (p.id, p.row, p.col, p.active)
        for p in game.blue.pawns + game.red.pawns
    ]

    assert new_positions == original_positions