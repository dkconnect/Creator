import json

from engine.game import Game
from engine.movement import Movement


def test_game_state_is_json_serializable():
    game = Game()

    state = game.to_dict()

    encoded = json.dumps(state)

    assert isinstance(encoded, str)


def test_game_state_contains_core_turn_data():
    game = Game()

    state = game.to_dict()

    assert state["board_size"] == 16
    assert state["current_player"] == "BLUE"
    assert state["turn_phase"] == Game.WAITING_FOR_ROLL
    assert state["dice"] is None
    assert state["selected_pawn_id"] is None
    assert state["game_over"] is False
    assert state["winner"] is None


def test_game_state_contains_pattern():
    game = Game()

    state = game.to_dict()

    assert state["pattern"]["name"] == game.pattern.name
    assert state["pattern"]["size"] == game.pattern.size
    assert state["pattern"]["grid"] == game.pattern.grid


def test_game_state_contains_all_pawns():
    game = Game()

    state = game.to_dict()

    blue_pawns = state["players"]["BLUE"]["pawns"]
    red_pawns = state["players"]["RED"]["pawns"]

    assert len(blue_pawns) == 32
    assert len(red_pawns) == 32

    assert len(blue_pawns) + len(red_pawns) == 64


def test_game_state_pawn_data_matches_engine():
    game = Game()

    state = game.to_dict()

    pawn = game.blue.pawns[0]
    pawn_state = state["players"]["BLUE"]["pawns"][0]

    assert pawn_state == {
        "id": pawn.id,
        "team": pawn.team,
        "row": pawn.row,
        "col": pawn.col,
        "active": pawn.active,
    }


def test_game_state_updates_after_dice_roll():
    game = Game()

    value = game.roll_dice()

    state = game.to_dict()

    assert state["dice"] == value

    if game.current_player == game.blue:
        assert state["turn_phase"] == Game.WAITING_FOR_SELECTION


def test_game_state_tracks_selected_pawn():
    game = Game()

    game.dice.value = 1
    game.turn_phase = Game.WAITING_FOR_SELECTION

    movable_pawn = None

    for pawn in game.current_player.pawns:
        if Movement.get_valid_moves_for_pawn(game, pawn):
            movable_pawn = pawn
            break

    assert movable_pawn is not None

    assert game.select_pawn(
        movable_pawn.row,
        movable_pawn.col
    )

    state = game.to_dict()

    assert state["selected_pawn_id"] == movable_pawn.id
    assert state["turn_phase"] == Game.WAITING_FOR_MOVE


def test_game_state_tracks_reserve_ids():
    game = Game()

    pawn = game.blue.pawns[0]

    game.blue.reserve.append(pawn)

    state = game.to_dict()

    assert pawn.id in state["players"]["BLUE"]["reserve"]