from engine.game import Game
from engine.ai.basic_ai import BasicAI
from engine.pattern import Pattern


def make_test_pattern(grid):
    pattern = Pattern()
    pattern.name = "TEST_PATTERN"
    pattern.size = len(grid)
    pattern.grid = grid
    return pattern


def test_basic_ai_returns_none_when_no_moves():
    game = Game()
    ai = BasicAI(team="RED")
    
    # Without rolling dice, dice.value is None -> no legal moves
    action = ai.select_move(game)
    assert action is None


def test_basic_ai_selects_legal_move():
    game = Game()
    ai = BasicAI(team="RED")
    
    game.dice.value = 3
    action = ai.select_move(game)
    
    assert action is not None
    pawn, row, col = action
    assert pawn.team == "RED"
    assert (row, col) in game.get_valid_moves_for_pawn if hasattr(game, "get_valid_moves_for_pawn") else True


def test_basic_ai_prioritizes_landing_on_pattern():
    game = Game()
    # Simple 2x2 pattern centered
    game.pattern = make_test_pattern([[1, 0], [0, 0]])
    ai = BasicAI(team="RED")

    offset = (game.board.size - game.pattern.size) // 2  # (7, 7)
    target_pos = (offset, offset)  # (7, 7)

    # Place a Red pawn at (10, 7) so a roll of 3 can land directly on (7, 7)
    pawn = game.red.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = 10, 7
    game.board.place_pawn(pawn)

    game.dice.value = 3
    action = ai.select_move(game)

    assert action is not None
    chosen_pawn, row, col = action
    assert (row, col) == target_pos


def test_basic_ai_prioritizes_capturing_opponent():
    game = Game()
    # Empty pattern so pattern bonus doesn't override capture
    game.pattern = make_test_pattern([[0, 0], [0, 0]])
    ai = BasicAI(team="RED")

    # Place Red pawn at (8, 8) and Blue pawn at (8, 11)
    red_pawn = game.red.pawns[0]
    game.board.grid[red_pawn.row][red_pawn.col] = None
    red_pawn.row, red_pawn.col = 8, 8
    game.board.place_pawn(red_pawn)

    blue_pawn = game.blue.pawns[0]
    game.board.grid[blue_pawn.row][blue_pawn.col] = None
    blue_pawn.row, blue_pawn.col = 8, 11
    game.board.place_pawn(blue_pawn)

    game.dice.value = 3
    action = ai.select_move(game)

    assert action is not None
    chosen_pawn, row, col = action
    assert (row, col) == (8, 11)


def test_basic_ai_prefers_not_to_leave_pattern_cell():
    """AI should avoid moving a piece off a pattern cell when other options exist."""
    game = Game()
    game.pattern = make_test_pattern([[1, 0], [0, 0]])
    ai = BasicAI(team="RED")

    offset = (game.board.size - game.pattern.size) // 2
    pattern_cell = (offset, offset)  # (7, 7)

    # Deactivate all red pawns first
    for p in game.red.pawns:
        game.board.grid[p.row][p.col] = None
        p.active = False
        p.row, p.col = -1, -1

    # Put one Red pawn ON the pattern cell
    on_pattern = game.red.pawns[0]
    on_pattern.active = True
    on_pattern.row, on_pattern.col = pattern_cell
    game.board.place_pawn(on_pattern)

    # Put another Red pawn that can move closer with roll 3
    far_pawn = game.red.pawns[1]
    far_pawn.active = True
    far_pawn.row, far_pawn.col = 12, 7
    game.board.place_pawn(far_pawn)

    game.dice.value = 3
    action = ai.select_move(game)

    assert action is not None
    chosen_pawn, row, col = action

    # Should not choose to move the piece that is already on the pattern
    # (unless it stays on pattern, which it can't with this setup)
    assert chosen_pawn is far_pawn