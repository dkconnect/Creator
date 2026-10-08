from engine.game import Game
from engine.action import GameAction
from engine.movement import Movement


def prepare_selected_move():
    game = Game()

    game.dice.value = 1
    game.turn_phase = Game.WAITING_FOR_SELECTION

    for pawn in game.current_player.pawns:
        moves = Movement.get_valid_moves_for_pawn(
            game,
            pawn
        )

        if not moves:
            continue

        assert game.select_pawn(
            pawn.row,
            pawn.col
        )

        row, col = moves[0]

        return game, pawn, row, col

    raise AssertionError("Expected at least one movable pawn")


def test_legal_action_is_accepted():
    game, pawn, row, col = prepare_selected_move()

    action = GameAction.move(
        pawn.id,
        row,
        col
    )

    assert game.is_legal_action(action)


def test_action_for_wrong_pawn_is_rejected():
    game, pawn, row, col = prepare_selected_move()

    other_pawn = next(
        p
        for p in game.current_player.pawns
        if p is not pawn
    )

    action = GameAction.move(
        other_pawn.id,
        row,
        col
    )

    assert not game.is_legal_action(action)


def test_illegal_destination_is_rejected():
    game, pawn, row, col = prepare_selected_move()

    action = GameAction.move(
        pawn.id,
        15,
        15
    )

    assert not game.is_legal_action(action)


def test_action_rejected_without_selection():
    game = Game()

    game.dice.value = 1
    game.turn_phase = Game.WAITING_FOR_SELECTION

    pawn = game.blue.pawns[0]

    action = GameAction.move(
        pawn.id,
        pawn.row,
        pawn.col
    )

    assert not game.is_legal_action(action)


def test_apply_action_moves_pawn():
    game, pawn, row, col = prepare_selected_move()

    old_row = pawn.row
    old_col = pawn.col

    action = GameAction.move(
        pawn.id,
        row,
        col
    )

    assert game.apply_action(action)

    assert game.board.get_pawn(
        old_row,
        old_col
    ) is None

    assert game.board.get_pawn(
        row,
        col
    ) is pawn


def test_apply_action_finishes_normal_turn():
    game, pawn, row, col = prepare_selected_move()

    action = GameAction.move(
        pawn.id,
        row,
        col
    )

    assert game.apply_action(action)

    if not game.game_over:
        assert game.current_player == game.red
        assert game.turn_phase == Game.WAITING_FOR_ROLL
        assert game.dice.value is None


def test_invalid_action_does_not_change_board():
    game, pawn, row, col = prepare_selected_move()

    original_positions = [
        (p.id, p.row, p.col, p.active)
        for p in game.blue.pawns + game.red.pawns
    ]

    action = GameAction.move(
        pawn.id,
        15,
        15
    )

    assert not game.apply_action(action)

    new_positions = [
        (p.id, p.row, p.col, p.active)
        for p in game.blue.pawns + game.red.pawns
    ]

    assert new_positions == original_positions