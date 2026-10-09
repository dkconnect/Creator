"""Unlimited capture respawns: captured pawns are never permanently removed."""
from engine.game import Game

def test_eleventh_capture_still_respawns():
    game = Game()
    pawn = game.red.pawns[0]
    # Make a free spawn slot.
    game.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = 7, 7
    game.board.place_pawn(pawn)
    game.red.captures_suffered = 10
    assert game.respawn_pawn(pawn)
    assert game.red.captures_suffered == 11
    assert pawn.active and game.board.get_pawn(pawn.row, pawn.col) is pawn

def test_reserve_after_tenth_respawn_is_not_deleted():
    game = Game()
    pawn = game.red.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    pawn.active = False
    pawn.row = pawn.col = -1
    game.red.reserve.append(pawn)
    game.red.respawns = 10
    assert game.process_reserve(game.red)
    assert pawn.active and pawn not in game.red.reserve
    assert game.red.respawns == 11

def test_full_spawn_rows_keep_pawn_in_reserve():
    game = Game()
    pawn = game.red.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    # Fill the vacated square with another pawn, ensuring no free spawn slot.
    from engine.pawn import Pawn
    game.board.place_pawn(Pawn(id=999, team="RED", row=pawn.row, col=pawn.col))
    pawn.row, pawn.col = 7, 7
    game.board.place_pawn(pawn)
    assert not game.respawn_pawn(pawn)
    assert pawn in game.red.reserve and not pawn.active
