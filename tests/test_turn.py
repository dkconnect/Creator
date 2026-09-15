from engine.game import Game
from engine.movement import Movement


def test_initial_turn_state():
    game = Game()

    assert game.current_player is game.blue
    assert game.turn_phase == Game.WAITING_FOR_ROLL
    assert game.selected_pawn is None
    assert game.game_over is False


def test_roll_dice_moves_to_selection_phase_when_legal_moves_exist():
    game = Game()

    value = game.roll_dice()

    assert value in range(1, 7)
    assert game.dice.value == value
    assert game.turn_phase == Game.WAITING_FOR_SELECTION


def test_roll_dice_returns_none_when_game_is_already_over():
    game = Game()
    game.game_over = True

    assert game.roll_dice() is None


def test_roll_dice_ignored_outside_waiting_for_roll_phase():
    game = Game()
    game.turn_phase = Game.WAITING_FOR_SELECTION

    assert game.roll_dice() is None


def test_select_pawn_ignored_before_dice_roll():
    game = Game()
    # Still WAITING_FOR_ROLL, selection shouldn't be allowed yet.
    pawn = game.blue.pawns[0]

    result = game.select_pawn(pawn.row, pawn.col)

    assert result is False
    assert game.selected_pawn is None


def test_select_pawn_rejects_opponent_pawn():
    game = Game()
    game.roll_dice()

    red_pawn = game.red.pawns[0]
    result = game.select_pawn(red_pawn.row, red_pawn.col)

    assert result is False
    assert game.selected_pawn is None
    assert game.turn_phase == Game.WAITING_FOR_SELECTION


def test_select_pawn_rejects_empty_square():
    game = Game()
    game.roll_dice()

    result = game.select_pawn(8, 8)  # center of board, empty at start

    assert result is False
    assert game.selected_pawn is None


def test_select_own_pawn_moves_to_move_phase():
    game = Game()
    game.roll_dice()

    # pawns[0] is a corner pawn and can be legally move-less on some
    # dice rolls; selection itself doesn't require a legal move though,
    # so this is safe regardless -- kept simple on purpose.
    pawn = game.current_player.pawns[0]
    result = game.select_pawn(pawn.row, pawn.col)

    assert result is True
    assert game.selected_pawn is pawn
    assert game.turn_phase == Game.WAITING_FOR_MOVE


def test_switch_turn_alternates_players_and_resets_phase():
    game = Game()
    game.roll_dice()
    game.dice.value = 3

    game.switch_turn()

    assert game.current_player is game.red
    assert game.turn_phase == Game.WAITING_FOR_ROLL
    assert game.selected_pawn is None
    assert game.dice.value is None

    game.switch_turn()

    assert game.current_player is game.blue


def test_move_selected_pawn_switches_turn_on_success():
    game = Game()

    pawn = game.blue.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = 8, 8
    game.board.place_pawn(pawn)

    game.dice.value = 3
    game.selected_pawn = pawn
    game.turn_phase = Game.WAITING_FOR_MOVE

    moved = game.move_selected_pawn(8, 11)

    assert moved is True
    assert game.current_player is game.red
    assert game.turn_phase == Game.WAITING_FOR_ROLL
    assert game.selected_pawn is None
    assert game.dice.value is None


def test_move_selected_pawn_rejects_illegal_destination():
    game = Game()

    pawn = game.blue.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = 8, 8
    game.board.place_pawn(pawn)

    game.dice.value = 3
    game.selected_pawn = pawn
    game.turn_phase = Game.WAITING_FOR_MOVE

    # (8, 8) with distance 3 in a straight/diagonal line never lands on
    # (9, 9 + 100) -- clearly outside any legal destination.
    moved = game.move_selected_pawn(9, 999)

    assert moved is False
    assert game.current_player is game.blue
    assert game.turn_phase == Game.WAITING_FOR_MOVE
    assert game.selected_pawn is pawn


def test_move_selected_pawn_ignored_outside_move_phase():
    game = Game()
    game.turn_phase = Game.WAITING_FOR_ROLL

    moved = game.move_selected_pawn(8, 8)

    assert moved is False


def test_roll_dice_auto_skips_turn_when_no_legal_move(monkeypatch):
    game = Game()

    monkeypatch.setattr(
        Movement, "player_has_legal_move", staticmethod(lambda g, p: False)
    )

    value = game.roll_dice()

    assert value in range(1, 7)
    # Turn should have been silently handed to the other player.
    assert game.current_player is game.red
    assert game.turn_phase == Game.WAITING_FOR_ROLL


def test_handle_click_selects_then_moves():
    game = Game()
    game.roll_dice()

    # Pick a pawn that actually has a legal move for this dice roll.
    # (A corner pawn like pawns[0] can have zero legal moves on some
    # rolls even though the team overall does -- that's expected.)
    pawn = next(
        p
        for p in game.current_player.pawns
        if Movement.get_valid_moves_for_pawn(game, p)
    )
    game.handle_click(pawn.row, pawn.col)

    assert game.selected_pawn is pawn
    assert game.turn_phase == Game.WAITING_FOR_MOVE

    valid_moves = game.get_valid_moves()
    assert valid_moves, "expected at least one legal move at game start"

    target_row, target_col = valid_moves[0]
    game.handle_click(target_row, target_col)

    assert game.selected_pawn is None
    assert game.turn_phase == Game.WAITING_FOR_ROLL