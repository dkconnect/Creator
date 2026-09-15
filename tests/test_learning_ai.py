from engine.game import Game
from engine.ai.learning_ai import LearningAI
from engine.pattern import Pattern


def make_test_pattern(grid):
    pattern = Pattern()
    pattern.name = "TEST_PATTERN"
    pattern.size = len(grid)
    pattern.grid = grid
    return pattern


def test_learning_ai_initial_weights():
    ai = LearningAI(team="RED")
    p_w, c_w, pr_w = ai._get_dynamic_weights()
    assert p_w == 100.0
    assert c_w == 40.0
    assert pr_w == 2.0


def test_learning_ai_adapts_to_aggressive_human():
    ai = LearningAI(team="RED")
    game = Game()

    # Simulate human capturing frequently
    for _ in range(5):
        ai.record_human_move(game, from_pos=(0, 0), to_pos=(5, 5), was_capture=True)

    p_w, c_w, pr_w = ai._get_dynamic_weights()
    # Against aggressive human, AI boosts pattern rushing
    assert p_w > 100.0
    assert c_w < 40.0


def test_learning_ai_adapts_to_pattern_rusher():
    game = Game()
    game.pattern = make_test_pattern([[1, 1], [1, 1]])
    offset = (game.board.size - game.pattern.size) // 2

    ai = LearningAI(team="RED")

    # Simulate human repeatedly moving into the pattern without capturing
    for _ in range(5):
        ai.record_human_move(game, from_pos=(0, 0), to_pos=(offset, offset), was_capture=False)

    p_w, c_w, pr_w = ai._get_dynamic_weights()
    # Against pattern rusher, AI boosts capture/disruption weight
    assert c_w > 40.0
    assert p_w < 100.0