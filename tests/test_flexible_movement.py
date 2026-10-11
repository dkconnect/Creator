from engine.game import Game
from engine.movement import Movement


def isolated_pawn(die=4):
    game = Game()
    pawn = game.blue.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = 8, 8
    game.board.place_pawn(pawn)
    game.dice.value = die
    return game, pawn


def test_all_shorter_distances_are_available():
    game, pawn = isolated_pawn(4)
    moves = Movement.get_valid_moves_for_pawn(game, pawn)
    for distance in range(1, 5):
        assert (8 - distance, 8) in moves
        assert (8, 8 + distance) in moves
    assert (3, 8) not in moves
    assert len(moves) == len(set(moves))


def test_eight_directions_one_step():
    game, pawn = isolated_pawn(1)
    assert len(Movement.get_valid_moves_for_pawn(game, pawn)) == 8


def test_friendly_destination_blocked_but_jump_still_allowed():
    game, pawn = isolated_pawn(4)
    friendly = game.blue.pawns[1]
    game.board.grid[friendly.row][friendly.col] = None
    friendly.row, friendly.col = 7, 8
    game.board.place_pawn(friendly)
    moves = Movement.get_valid_moves_for_pawn(game, pawn)
    assert (7, 8) not in moves
    assert (6, 8) in moves


def test_enemy_capture_square_available_at_shorter_distance():
    game, pawn = isolated_pawn(4)
    enemy = game.red.pawns[0]
    game.board.grid[enemy.row][enemy.col] = None
    enemy.row, enemy.col = 7, 8
    game.board.place_pawn(enemy)
    assert (7, 8) in Movement.get_valid_moves_for_pawn(game, pawn)


def test_die_one_to_six_and_board_bounds():
    for die in range(1, 7):
        game, pawn = isolated_pawn(die)
        for r, c in Movement.get_valid_moves_for_pawn(game, pawn):
            assert 0 <= r < game.board.size and 0 <= c < game.board.size
            assert 1 <= max(abs(r - pawn.row), abs(c - pawn.col)) <= die
