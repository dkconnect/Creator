from engine.game import Game


def remove_from_board(game, pawn):
    game.board.grid[pawn.row][pawn.col] = None


def test_capture_removes_opponent_from_destination():
    game = Game()

    blue = game.blue.pawns[0]
    red = game.red.pawns[0]

    remove_from_board(game, blue)
    remove_from_board(game, red)

    blue.row = 8
    blue.col = 8
    red.row = 8
    red.col = 11

    game.board.place_pawn(blue)
    game.board.place_pawn(red)

    game.dice.value = 3
    game.selected_pawn = blue
    game.turn_phase = game.WAITING_FOR_MOVE

    assert (8, 11) in game.get_valid_moves()

    game.move_selected_pawn(8, 11)

    assert game.board.get_pawn(8, 11) == blue
    assert red.active is True
    assert game.red.respawns == 1


def test_captured_pawn_respawns_in_first_empty_blue_spawn():
    game = Game()

    blue = game.blue.pawns[0]
    red = game.red.pawns[0]

    remove_from_board(game, blue)
    remove_from_board(game, red)

    blue.row = 8
    blue.col = 8
    red.row = 8
    red.col = 11

    game.board.place_pawn(blue)
    game.board.place_pawn(red)

    game.dice.value = 3
    game.selected_pawn = blue
    game.turn_phase = game.WAITING_FOR_MOVE

    game.move_selected_pawn(8, 11)
    respawned = red

    assert respawned.row == 14
    assert respawned.col == 0

def test_respawn_uses_first_empty_spawn_square():
    game = Game()

    captured = game.red.pawns[0]

    remove_from_board(game, captured)

    # Free the first Red spawn square.
    game.board.grid[14][0] = None

    game.respawn_pawn(captured)

    assert captured.row == 14
    assert captured.col == 0

def test_first_ten_captures_respawn():
    game = Game()

    for i in range(10):
        pawn = game.red.pawns[i]

        remove_from_board(game, pawn)

        result = game.respawn_pawn(pawn)

        assert result is True
        assert pawn.active is True

    assert game.red.respawns == 10


def test_eleventh_capture_is_permanent():
    game = Game()

    for i in range(10):
        pawn = game.red.pawns[i]

        remove_from_board(game, pawn)
        game.respawn_pawn(pawn)

    eleventh = game.red.pawns[10]

    remove_from_board(game, eleventh)

    result = game.respawn_pawn(eleventh)

    assert result is False
    assert eleventh.active is False
    assert game.red.captures_suffered == 11
    assert game.red.respawns == 10


def test_respawn_counter_is_shared_by_team():
    game = Game()

    first_pawn = game.red.pawns[0]
    second_pawn = game.red.pawns[1]

    remove_from_board(game, first_pawn)
    game.respawn_pawn(first_pawn)

    remove_from_board(game, second_pawn)
    game.respawn_pawn(second_pawn)

    assert game.red.respawns == 2


def test_eleventh_capture_can_be_any_pawn():
    game = Game()

    # Use ten different pawns for the first ten captures.
    for i in range(10):
        pawn = game.red.pawns[i]

        remove_from_board(game, pawn)
        game.respawn_pawn(pawn)

    # The 11th capture is a completely different pawn.
    eleventh = game.red.pawns[20]

    remove_from_board(game, eleventh)

    result = game.respawn_pawn(eleventh)

    assert result is False
    assert eleventh.active is False

    # The 11th capture is a permanent removal, not a respawn, so the
    # respawn count stays at 10 ("Only successful respawns count").
    assert game.red.respawns == 10


def test_active_pawn_can_be_captured_and_respawned_again():
    game = Game()

    pawn = game.red.pawns[0]

    remove_from_board(game, pawn)

    game.respawn_pawn(pawn)

    assert pawn.active is True
    assert game.red.respawns == 1

    remove_from_board(game, pawn)

    game.respawn_pawn(pawn)

    assert pawn.active is True
    assert game.red.respawns == 2