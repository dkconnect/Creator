import pytest
from engine.game import Game
from engine.movement import Movement
from engine.ai.advanced_ai import AdvancedAI


def test_hypothetical_roll_is_independent_of_live_dice():
    game = Game()
    pawn = game.blue.pawns[0]
    game.dice.value = 1
    one = Movement.get_valid_moves_for_pawn(game, pawn)
    six = Movement.get_valid_moves_for_pawn(game, pawn, dice_value=6)
    assert game.dice.value == 1
    assert set(one) <= set(six)
    assert len(six) > len(one)


@pytest.mark.parametrize("team", ["BLUE", "RED"])
def test_advanced_ai_opponent_forecast_does_not_change_dice(team):
    game = Game()
    game.dice.value = 3
    ai = AdvancedAI(team)
    ai._evaluate_human_chance_node(game, ai._get_target_pattern_cells(game))
    assert game.dice.value == 3


def test_advanced_ai_select_move_does_not_change_dice(monkeypatch):
    game = Game()
    game.dice.value = 2
    monkeypatch.setattr(AdvancedAI, "_evaluate_human_chance_node", lambda self, game, cells: 0.0)
    AdvancedAI("RED").select_move(game)
    assert game.dice.value == 2
