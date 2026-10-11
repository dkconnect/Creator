from engine.game import Game
from engine.pattern import Pattern
from engine.pawn import Pawn
from engine.movement import Movement
from engine import victory


def pattern(grid):
    p = Pattern()
    p.name = "TEST"
    p.size = len(grid)
    p.grid = grid
    return p


def test_full_formation_only():
    g = Game()
    g.pattern = pattern([[1, 1], [1, 1]])
    targets = victory.target_cells(g, "BLUE")
    assert targets == victory.target_cells(g, "RED")
    for i, (r, c) in enumerate(targets[:3]):
        g.board.place_pawn(Pawn(id=5000+i, team="BLUE", row=r, col=c))
    assert not victory.check_victory(g, g.blue)
    r, c = targets[3]
    g.board.place_pawn(Pawn(id=5004, team="BLUE", row=r, col=c))
    assert victory.check_victory(g, g.blue)


def test_flexible_distance_up_to_roll():
    g = Game()
    pawn = g.blue.pawns[0]
    g.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = 8, 8
    g.board.place_pawn(pawn)
    g.dice.value = 4
    moves = Movement.get_valid_moves_for_pawn(g, pawn)
    assert (4, 8) in moves
    assert (7, 8) in moves
    assert all(1 <= max(abs(r-8), abs(c-8)) <= 4 for r,c in moves)


def test_turn_400_does_not_end_match():
    g = Game()
    g.turn_count = 399
    g.switch_turn()
    assert g.turn_count == 400
    assert not g.game_over
    assert g.winner is None
    g.switch_turn()
    assert g.turn_count == 401
    assert not g.game_over
    assert g.to_dict()["turn_limit"] is None
