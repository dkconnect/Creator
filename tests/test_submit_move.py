from engine.game import Game
from engine.movement import Movement


def prepare_game():
    game = Game()

    game.dice.value = 1
    game.turn_phase = Game.WAITING_FOR_SELECTION

    return game


def find_movable_pawn(game):
    """
    Find a current-player pawn that actually has
    at least one legal move.
    """

    for pawn in game.current_player.pawns:
        moves = Movement.get_valid_moves_for_pawn(
            game,
            pawn
        )

        if moves:
            return pawn, moves[0]

    raise AssertionError("Expected at least one movable pawn")


def test_submit_move_executes_legal_move():
    game = prepare_game()

    pawn, destination = find_movable_pawn(game)
    row, col = destination

    old_row = pawn.row
    old_col = pawn.col

    assert game.submit_move(
        pawn.id,
        row,
        col
    )

    assert game.board.get_pawn(
        old_row,
        old_col
    ) is None

    assert game.board.get_pawn(
        row,
        col
    ) is pawn


def test_submit_move_rejects_wrong_player_pawn():
    game = prepare_game()

    pawn = game.red.pawns[0]

    result = game.submit_move(
        pawn.id,
        10,
        10
    )

    assert result is False
    assert game.current_player == game.blue
    assert game.turn_phase == Game.WAITING_FOR_SELECTION


def test_submit_move_rejects_unknown_pawn():
    game = prepare_game()

    assert not game.submit_move(
        9999,
        5,
        5
    )

    assert game.selected_pawn is None
    assert game.turn_phase == Game.WAITING_FOR_SELECTION


def test_submit_move_rejects_illegal_destination():
    game = prepare_game()

    pawn, _ = find_movable_pawn(game)

    old_row = pawn.row
    old_col = pawn.col

    assert not game.submit_move(
        pawn.id,
        15,
        15
    )

    assert pawn.row == old_row
    assert pawn.col == old_col

    assert game.selected_pawn is None
    assert game.turn_phase == Game.WAITING_FOR_SELECTION


def test_submit_move_rejected_before_dice_roll():
    game = Game()

    pawn = game.blue.pawns[0]

    assert not game.submit_move(
        pawn.id,
        5,
        5
    )

    assert game.turn_phase == Game.WAITING_FOR_ROLL


def test_submit_move_rejected_after_game_over():
    game = prepare_game()

    pawn = game.blue.pawns[0]

    game.game_over = True

    assert not game.submit_move(
        pawn.id,
        5,
        5
    )


def test_submit_move_finishes_normal_turn():
    game = prepare_game()

    pawn, destination = find_movable_pawn(game)
    row, col = destination

    assert game.submit_move(
        pawn.id,
        row,
        col
    )

    if not game.game_over:
        assert game.current_player == game.red
        assert game.turn_phase == Game.WAITING_FOR_ROLL
        assert game.dice.value is None