from engine.game import Game


def test_captured_pawn_enters_reserve_when_spawn_is_full():
    game = Game()

    captured = game.red.pawns[0]

    # Remove the pawn from its current position.
    game.board.grid[captured.row][captured.col] = None

    # Make every Red spawn cell occupied, including the square the
    # captured pawn just vacated (otherwise that square itself counts
    # as "an empty cell in its home spawn region" and it respawns there).
    blocker = game.blue.pawns[0]
    game.board.grid[captured.row][captured.col] = blocker

    result = game.respawn_pawn(captured)

    assert result is False
    assert captured.active is False
    assert captured in game.red.reserve
    assert game.red.captures_suffered == 1
    assert game.red.respawns == 0


def test_reserved_pawn_spawns_when_space_becomes_available():
    game = Game()

    captured = game.red.pawns[0]

    game.board.grid[captured.row][captured.col] = None

    # Block the captured pawn's own vacated square so the spawn is
    # genuinely full and it's forced into the reserve.
    blocker = game.blue.pawns[0]
    game.board.grid[captured.row][captured.col] = blocker

    game.respawn_pawn(captured)

    assert captured in game.red.reserve

    # Make the first Red spawn square available.
    game.board.grid[14][0] = None

    result = game.process_reserve(game.red)

    assert result is True
    assert captured not in game.red.reserve
    assert captured.active is True
    assert captured.row == 14
    assert captured.col == 0
    assert game.red.respawns == 1


def test_reserve_uses_first_empty_spawn_square():
    game = Game()

    captured = game.red.pawns[0]

    # Temporarily make every red spawn square occupied.
    # Move captured pawn out of its original square first,
    # then put another pawn there if necessary.
    game.board.grid[captured.row][captured.col] = None

    # Fill the now-empty spawn square.
    blocker = game.blue.pawns[0]
    game.board.grid[14][0] = blocker

    result = game.respawn_pawn(captured)

    assert result is False
    assert captured in game.red.reserve

    # Free the third spawn square.
    game.board.grid[14][2] = None

    result = game.process_reserve(game.red)

    assert result is True
    assert captured.row == 14
    assert captured.col == 2


def test_reserve_processes_oldest_pawn_first():
    game = Game()

    first = game.red.pawns[0]
    second = game.red.pawns[1]

    # Block both vacated squares so both captures are forced into reserve.
    blocker_a = game.blue.pawns[0]
    blocker_b = game.blue.pawns[1]

    game.board.grid[first.row][first.col] = None
    game.board.grid[first.row][first.col] = blocker_a
    game.respawn_pawn(first)

    game.board.grid[second.row][second.col] = None
    game.board.grid[second.row][second.col] = blocker_b
    game.respawn_pawn(second)

    assert game.red.reserve[0] == first
    assert game.red.reserve[1] == second

    # Free one spawn square.
    game.board.grid[14][0] = None

    game.process_reserve(game.red)

    assert first.active is True
    assert first.row == 14
    assert first.col == 0

    assert second in game.red.reserve


def test_reserved_pawn_counts_as_capture():
    game = Game()

    captured = game.red.pawns[0]

    game.board.grid[captured.row][captured.col] = None

    # Block the vacated square so this capture is genuinely forced
    # into the reserve rather than respawning in place.
    blocker = game.blue.pawns[0]
    game.board.grid[captured.row][captured.col] = blocker

    game.respawn_pawn(captured)

    assert game.red.captures_suffered == 1
    assert game.red.respawns == 0

    # Later it gets a spawn.
    game.board.grid[14][0] = None

    game.process_reserve(game.red)

    assert game.red.captures_suffered == 1
    assert game.red.respawns == 1
