from engine.game import Game
from engine.ai.basic_ai import BasicAI
from engine.ai.learning_ai import LearningAI
from engine.ai.advanced_ai import AdvancedAI


def test_ai_blocks_human_click_during_ai_turn():
    ai = BasicAI(team="RED")
    game = Game(ai_controller=ai)

    # Move to RED's turn
    game.switch_turn()
    assert game.current_player == game.red

    # Human attempts to click/select a Red pawn directly
    red_pawn = game.red.pawns[0]
    game.handle_click(red_pawn.row, red_pawn.col)

    # Click should be blocked
    assert game.selected_pawn is None


def test_step_ai_executes_complete_turn():
    ai = BasicAI(team="RED")
    game = Game(ai_controller=ai)

    # Switch to RED turn
    game.switch_turn()
    assert game.current_player == game.red
    assert game.turn_phase == Game.WAITING_FOR_ROLL

    # Execute step_ai
    performed = game.step_ai()

    # Verify that either a move was made or turn was auto-skipped if no moves
    assert game.current_player == game.blue
    assert game.turn_phase == Game.WAITING_FOR_ROLL


def test_learning_ai_records_human_moves_via_game_loop():
    ai = LearningAI(team="RED")
    game = Game(ai_controller=ai)

    # Blue (human) takes a turn
    pawn = game.blue.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = 8, 8
    game.board.place_pawn(pawn)

    game.dice.value = 3
    game.selected_pawn = pawn
    game.turn_phase = Game.WAITING_FOR_MOVE

    game.move_selected_pawn(8, 11)

    assert ai.human_moves_count == 1