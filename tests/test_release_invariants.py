"""Step 58: frozen-rule release guardrails (no UI or gameplay modifications)."""
import pytest

from engine.game import Game
from engine.movement import Movement
from engine import victory
from engine.ai.basic_ai import BasicAI
from engine.ai.advanced_ai import AdvancedAI


def test_complete_formation_is_required_and_shared_by_both_teams():
    game = Game()
    assert victory.VICTORY_FRACTION == 1.0
    assert set(victory.target_cells(game, 'RED')) == {
        (game.board.size - 1 - r, c)
        for r, c in victory.target_cells(game, 'BLUE')
    }
    assert victory.required_count(game) == len(victory.target_cells(game, 'BLUE'))


def test_no_turn_based_winner_even_after_1000_turns():
    game = Game()
    game.turn_count = 1001
    assert victory.endgame_result(game) is None
    assert not game.game_over


@pytest.mark.parametrize('roll', range(1, 7))
def test_flexible_moves_do_not_mutate_dice(roll):
    game = Game()
    pawn = game.blue.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = 8, 8
    game.board.place_pawn(pawn)
    game.dice.value = roll
    moves = Movement.get_valid_moves_for_pawn(game, pawn)
    assert (8 - roll, 8) in moves
    assert (7, 8) in moves
    if roll < 6:
        assert (8 - roll - 1, 8) not in moves
    assert game.dice.value == roll


@pytest.mark.parametrize('ai_type', [BasicAI, AdvancedAI])
def test_ai_cannot_change_live_roll(ai_type):
    game = Game()
    game.dice.value = 4
    ai = ai_type('BLUE')
    ai.select_move(game)
    assert game.dice.value == 4
