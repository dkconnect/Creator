from engine.game import Game
from engine.movement import Movement


def setup_game_with_pawn(row, col, dice_value):
    game = Game()

    pawn = game.blue.pawns[0]

    game.board.grid[pawn.row][pawn.col] = None

    pawn.row = row
    pawn.col = col

    game.board.place_pawn(pawn)

    game.dice.value = dice_value
    game.selected_pawn = pawn

    return game, pawn


def test_moves_up():
    game, pawn = setup_game_with_pawn(8, 8, 3)

    moves = Movement.get_valid_moves(game)

    assert (5, 8) in moves


def test_moves_down():
    game, pawn = setup_game_with_pawn(8, 8, 3)

    moves = Movement.get_valid_moves(game)

    assert (11, 8) in moves


def test_moves_left():
    game, pawn = setup_game_with_pawn(8, 8, 3)

    moves = Movement.get_valid_moves(game)

    assert (8, 5) in moves


def test_moves_right():
    game, pawn = setup_game_with_pawn(8, 8, 3)

    moves = Movement.get_valid_moves(game)

    assert (8, 11) in moves


def test_moves_up_left():
    game, pawn = setup_game_with_pawn(8, 8, 3)

    moves = Movement.get_valid_moves(game)

    assert (5, 5) in moves


def test_moves_up_right():
    game, pawn = setup_game_with_pawn(8, 8, 3)

    moves = Movement.get_valid_moves(game)

    assert (5, 11) in moves


def test_moves_down_left():
    game, pawn = setup_game_with_pawn(8, 8, 3)

    moves = Movement.get_valid_moves(game)

    assert (11, 5) in moves


def test_moves_down_right():
    game, pawn = setup_game_with_pawn(8, 8, 3)

    moves = Movement.get_valid_moves(game)

    assert (11, 11) in moves


def test_movement_is_exact_distance():
    game, pawn = setup_game_with_pawn(8, 8, 4)

    moves = Movement.get_valid_moves(game)

    assert (4, 8) in moves
    assert (3, 8) not in moves
    assert (5, 8) not in moves


def test_jumping_over_pawns_is_allowed():
    game, pawn = setup_game_with_pawn(8, 8, 4)

    # Put another pawn between the moving pawn and destination.
    blocker = game.red.pawns[0]

    game.board.grid[blocker.row][blocker.col] = None

    blocker.row = 6
    blocker.col = 8

    game.board.place_pawn(blocker)

    moves = Movement.get_valid_moves(game)

    assert (4, 8) in moves


def test_friendly_pawn_destination_is_illegal():
    game, pawn = setup_game_with_pawn(8, 8, 3)

    friendly = game.blue.pawns[1]

    game.board.grid[friendly.row][friendly.col] = None

    friendly.row = 5
    friendly.col = 8

    game.board.place_pawn(friendly)

    moves = Movement.get_valid_moves(game)

    assert (5, 8) not in moves


def test_enemy_pawn_destination_is_legal():
    game, pawn = setup_game_with_pawn(8, 8, 3)

    enemy = game.red.pawns[0]

    game.board.grid[enemy.row][enemy.col] = None

    enemy.row = 5
    enemy.col = 8

    game.board.place_pawn(enemy)

    moves = Movement.get_valid_moves(game)

    assert (5, 8) in moves


def test_move_outside_board_is_illegal():
    game, pawn = setup_game_with_pawn(1, 14, 3)

    # Clear the friendly pawn sitting at (1, 11) — it's part of the
    # initial setup and would otherwise block that destination.
    game.board.grid[1][11] = None

    moves = Movement.get_valid_moves(game)

    # Up is outside the board.
    assert (-2, 14) not in moves

    # Right is outside the board.
    assert (1, 17) not in moves

    # These are still valid.
    assert (4, 14) in moves
    assert (1, 11) in moves
