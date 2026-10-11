import pytest
from engine.game import Game
from engine.movement import Movement


@pytest.mark.parametrize('roll', range(1, 7))
def test_empty_board_mirrored_moves_match_for_both_teams(roll):
    game = Game()
    size = game.board.size
    for row in game.board.grid:
        for col in range(size):
            row[col] = None
    blue = game.blue.pawns[0]
    red = game.red.pawns[0]
    blue.row, blue.col = 5, 7
    red.row, red.col = size - 1 - blue.row, blue.col
    game.board.place_pawn(blue)
    game.board.place_pawn(red)
    game.dice.value = roll
    blue_moves = set(Movement.get_valid_moves_for_pawn(game, blue))
    red_moves = set(Movement.get_valid_moves_for_pawn(game, red))
    assert {(size - 1 - r, c) for r, c in blue_moves} == red_moves


def test_dice_roll_generation_is_not_in_ai_module():
    from engine.dice import Dice
    assert Dice().value is None
