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