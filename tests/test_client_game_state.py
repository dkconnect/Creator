from engine.game import Game
from network.client_game_state import ClientGameState


def make_state():
    return Game().to_dict()


def test_client_state_defaults():
    state = ClientGameState()

    assert state.board_size == 16
    assert state.current_player is None
    assert state.turn_phase is None
    assert state.dice is None
    assert state.selected_pawn_id is None
    assert state.game_over is False
    assert state.winner is None
    assert state.pattern is None
    assert state.players is None


def test_client_state_accepts_game_state():
    state = ClientGameState()

    game_state = make_state()

    assert state.update(
        game_state
    )

    assert state.board_size == 16
    assert state.current_player == "BLUE"
    assert state.turn_phase == "WAITING_FOR_ROLL"
    assert state.dice is None
    assert state.game_over is False


def test_client_state_stores_pattern():
    state = ClientGameState()

    game_state = make_state()

    state.update(
        game_state
    )

    assert state.pattern == (
        game_state["pattern"]
    )


def test_client_state_stores_players():
    state = ClientGameState()

    game_state = make_state()

    state.update(
        game_state
    )

    assert state.players == (
        game_state["players"]
    )

    assert len(
        state.players["BLUE"]["pawns"]
    ) == 32

    assert len(
        state.players["RED"]["pawns"]
    ) == 32


def test_client_state_rejects_non_dictionary():
    state = ClientGameState()

    assert not state.update(
        None
    )


def test_client_state_rejects_incomplete_state():
    state = ClientGameState()

    assert not state.update(
        {
            "board_size": 16
        }
    )