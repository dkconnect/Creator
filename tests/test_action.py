from engine.action import GameAction


def test_create_move_action():
    action = GameAction.move(
        pawn_id=37,
        row=8,
        col=11
    )

    assert action.action_type == GameAction.MOVE
    assert action.pawn_id == 37
    assert action.row == 8
    assert action.col == 11


def test_action_to_dict():
    action = GameAction.move(
        pawn_id=12,
        row=5,
        col=9
    )

    data = action.to_dict()

    assert data == {
        "type": "MOVE",
        "pawn_id": 12,
        "row": 5,
        "col": 9,
    }


def test_action_from_dict():
    data = {
        "type": "MOVE",
        "pawn_id": 42,
        "row": 10,
        "col": 4,
    }

    action = GameAction.from_dict(data)

    assert action == GameAction.move(
        pawn_id=42,
        row=10,
        col=4
    )


def test_action_round_trip():
    original = GameAction.move(
        pawn_id=7,
        row=6,
        col=13
    )

    restored = GameAction.from_dict(
        original.to_dict()
    )

    assert restored == original