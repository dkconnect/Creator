"""Step 55: a die is a maximum movement distance, not an exact distance."""
from engine.game import Game
from engine.movement import Movement


def isolated(die):
    game = Game()
    pawn = game.blue.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = 8, 8
    game.board.place_pawn(pawn)
    game.dice.value = die
    return game, pawn


def test_each_roll_allows_every_shorter_distance():
    for die in range(1, 7):
        game, pawn = isolated(die)
        moves = set(Movement.get_valid_moves_for_pawn(game, pawn))
        for distance in range(1, die + 1):
            assert (8 - distance, 8) in moves
            assert (8, 8 + distance) in moves
            assert (8 - distance, 8 + distance) in moves
        assert (8 - die - 1, 8) not in moves
        assert len(moves) == len(Movement.get_valid_moves_for_pawn(game, pawn))


def test_friendly_landing_blocked_but_jump_allowed():
    game, pawn = isolated(4)
    friend = game.blue.pawns[1]
    game.board.grid[friend.row][friend.col] = None
    friend.row, friend.col = 7, 8
    game.board.place_pawn(friend)
    moves = Movement.get_valid_moves_for_pawn(game, pawn)
    assert (7, 8) not in moves
    assert (6, 8) in moves
    assert (4, 8) in moves


def test_enemy_landing_is_capturable_at_shorter_distance():
    game, pawn = isolated(6)
    enemy = game.red.pawns[0]
    game.board.grid[enemy.row][enemy.col] = None
    enemy.row, enemy.col = 6, 8
    game.board.place_pawn(enemy)
    assert (6, 8) in Movement.get_valid_moves_for_pawn(game, pawn)
