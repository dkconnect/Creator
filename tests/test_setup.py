from engine.game import Game


def test_board_is_16x16():
    game = Game()

    assert game.board.size == 16
    assert len(game.board.grid) == 16
    assert all(len(row) == 16 for row in game.board.grid)


def test_each_player_starts_with_32_pawns():
    game = Game()

    assert len(game.blue.pawns) == 32
    assert len(game.red.pawns) == 32


def test_blue_starts_on_rows_zero_and_one():
    game = Game()

    for pawn in game.blue.pawns:
        assert pawn.row in (0, 1)


def test_red_starts_on_rows_fourteen_and_fifteen():
    game = Game()

    for pawn in game.red.pawns:
        assert pawn.row in (14, 15)


def test_all_starting_pawns_are_active():
    game = Game()

    for pawn in game.blue.pawns:
        assert pawn.active is True

    for pawn in game.red.pawns:
        assert pawn.active is True


def test_blue_starts_first():
    game = Game()

    assert game.current_player == game.blue


def test_each_spawn_cell_contains_one_pawn():
    game = Game()

    for row in range(2):
        for col in range(16):
            assert game.board.get_pawn(row, col) is not None

    for row in range(14, 16):
        for col in range(16):
            assert game.board.get_pawn(row, col) is not None


def test_initial_respawn_counts_are_zero():
    game = Game()

    assert game.blue.respawns == 0
    assert game.red.respawns == 0


def test_initial_reserves_are_empty():
    game = Game()

    assert game.blue.reserve == []
    assert game.red.reserve == []
