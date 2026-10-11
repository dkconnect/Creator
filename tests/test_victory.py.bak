from engine.game import Game
from engine.pattern import Pattern
from engine.pawn import Pawn
import engine.victory as victory


SIMPLE_GRID = [
    [1, 1],
    [1, 1],
]


def make_pattern(grid):
    pattern = Pattern()
    pattern.name = "TEST"
    pattern.size = len(grid)
    pattern.grid = grid
    return pattern


def centered_offset(game):
    return (game.board.size - game.pattern.size) // 2


def fill_pattern_for_team(game, team, extra_id_start=9000):
    """Place a pawn of `team` on every '1' cell of game.pattern, centered
    on the board, as the win condition expects."""
    offset = centered_offset(game)

    for row in range(game.pattern.size):
        for col in range(game.pattern.size):
            if game.pattern.grid[row][col] == 0:
                continue

            board_row = row + offset
            board_col = col + offset

            pawn = Pawn(
                id=extra_id_start + row * game.pattern.size + col,
                team=team,
                row=board_row,
                col=board_col,
            )
            game.board.place_pawn(pawn)


def test_victory_true_when_pattern_filled_by_same_team():
    game = Game()
    game.pattern = make_pattern(SIMPLE_GRID)

    fill_pattern_for_team(game, "BLUE")

    assert victory.check_victory(game, game.blue) is True


def test_victory_false_when_a_required_cell_is_empty():
    game = Game()
    game.pattern = make_pattern(SIMPLE_GRID)

    fill_pattern_for_team(game, "BLUE")

    offset = centered_offset(game)
    game.board.grid[offset][offset] = None

    assert victory.check_victory(game, game.blue) is False


def test_victory_false_when_a_required_cell_belongs_to_opponent():
    game = Game()
    game.pattern = make_pattern(SIMPLE_GRID)

    fill_pattern_for_team(game, "BLUE")

    offset = centered_offset(game)
    game.board.grid[offset][offset] = Pawn(
        id=8000, team="RED", row=offset, col=offset
    )

    assert victory.check_victory(game, game.blue) is False


def test_victory_ignores_cells_outside_the_pattern():
    # Cells marked 0 in the pattern shouldn't matter at all, even if
    # they're empty or held by the opponent.
    game = Game()
    game.pattern = make_pattern(SIMPLE_GRID)

    fill_pattern_for_team(game, "BLUE")

    # Board start already has plenty of non-pattern cells occupied by
    # both teams (rows 0-1 and 14-15) -- victory should still hold.
    assert victory.check_victory(game, game.blue) is True


def test_victory_pattern_is_centered_not_pinned_to_a_corner():
    """Regression test for the centering bug: the win condition must
    check cells around the middle of the board, not the bottom-right
    corner (old, buggy offset = board.size - pattern.size)."""
    game = Game()
    game.pattern = make_pattern(SIMPLE_GRID)

    offset = centered_offset(game)
    buggy_offset = game.board.size - game.pattern.size

    # These offsets must differ for this test to be meaningful.
    assert offset != buggy_offset

    fill_pattern_for_team(game, "BLUE")

    # Pawns were placed at the *centered* offset only, so victory should
    # be true. If the bug reappears (offset not divided by 2), the code
    # would look at the corner instead and incorrectly return False.
    assert victory.check_victory(game, game.blue) is True


def test_victory_with_real_loaded_pattern_from_disk():
    # Integration check: use whatever pattern Game() actually loaded
    # from the patterns/ folder, not a hand-built one.
    game = Game()

    fill_pattern_for_team(game, "BLUE")

    assert victory.check_victory(game, game.blue) is True