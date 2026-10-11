from engine.game import Game
from engine.ai.advanced_ai import AdvancedAI
from engine.pattern import Pattern


def make_test_pattern(grid):
    pattern = Pattern()
    pattern.name = "TEST_PATTERN"
    pattern.size = len(grid)
    pattern.grid = grid
    return pattern


def test_advanced_ai_takes_immediate_win():
    game = Game()
    # 1-cell target pattern
    game.pattern = make_test_pattern([[1]])
    offset = (game.board.size - game.pattern.size) // 2  # (7, 7)

    ai = AdvancedAI(team="RED")

    # Place red pawn 3 cells away at (10, 7)
    pawn = game.red.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = 10, 7
    game.board.place_pawn(pawn)

    game.dice.value = 3
    action = ai.select_move(game)

    assert action is not None
    chosen_pawn, tr, tc = action
    assert (tr, tc) == (offset, offset)


def test_advanced_ai_preserves_dice_and_board_state():
    game = Game()
    ai = AdvancedAI(team="RED")

    game.dice.value = 4
    initial_pawn_positions = [
        (p.id, p.row, p.col, p.active) for p in game.red.pawns + game.blue.pawns
    ]

    action = ai.select_move(game)

    # Verify simulation leaves the dice value intact
    assert game.dice.value == 4

    # Verify all pawns return to original coordinates before actual execution
    current_pawn_positions = [
        (p.id, p.row, p.col, p.active) for p in game.red.pawns + game.blue.pawns
    ]
    assert initial_pawn_positions == current_pawn_positions