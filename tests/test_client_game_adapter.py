from engine.game import Game
from network.client_game_state import ClientGameState
from network.client_game_adapter import ClientGameAdapter


def make_adapter():
    game = Game()
    state = ClientGameState()

    assert state.update(
        game.to_dict()
    )

    return game, state, ClientGameAdapter(state)


def test_board_dimensions():
    _, _, adapter = make_adapter()

    assert adapter.board.size == 16
    assert len(adapter.board.grid) == 16


def test_blue_pawn():
    _, _, adapter = make_adapter()

    assert adapter.board.get_pawn(0, 0).id == 0


def test_red_pawn():
    _, _, adapter = make_adapter()

    assert adapter.board.get_pawn(14, 0).id == 32


def test_current_player():
    _, _, adapter = make_adapter()

    assert adapter.current_player.team == "BLUE"


def test_dice_refresh():
    game, state, adapter = make_adapter()

    game.dice.value = 5

    state.update(
        game.to_dict()
    )

    adapter.refresh()

    assert adapter.dice.value == 5


def test_selected_pawn():
    game, state, adapter = make_adapter()

    game.dice.value = 1
    game.turn_phase = game.WAITING_FOR_SELECTION

    assert game.select_pawn(1, 0)

    state.update(
        game.to_dict()
    )

    adapter.refresh()

    assert (
        adapter.selected_pawn.id
        == game.selected_pawn.id
    )


def test_pattern():
    game, _, adapter = make_adapter()

    assert adapter.pattern.grid == game.pattern.grid


def test_winner():
    game, state, adapter = make_adapter()

    game.game_over = True
    game.winner = game.blue

    state.update(
        game.to_dict()
    )

    adapter.refresh()

    assert adapter.game_over
    assert adapter.winner.team == "BLUE"


def test_board_refresh_and_legal_moves():
    game, state, adapter = make_adapter()

    pawn = game.blue.pawns[0]

    game.board.grid[
        pawn.row
    ][pawn.col] = None

    pawn.row, pawn.col = 5, 5

    game.board.grid[5][5] = pawn

    game.dice.value = 1
    game.turn_phase = game.WAITING_FOR_SELECTION

    assert game.select_pawn(5, 5)

    state.update(
        game.to_dict()
    )

    adapter.refresh()

    assert adapter.board.get_pawn(0, 0) is None
    assert adapter.board.get_pawn(5, 5).id == pawn.id

    assert (
        adapter.get_valid_moves()
        == game.get_valid_moves()
    )