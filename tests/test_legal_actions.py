from engine.game import Game


def test_legal_actions_empty_before_dice_roll():
    game = Game()

    actions = game.get_legal_actions()

    assert actions == []


def test_legal_actions_returns_current_player_moves():
    game = Game()

    game.dice.value = 1

    actions = game.get_legal_actions()

    assert len(actions) > 0

    for pawn, row, col in actions:
        assert pawn.team == "BLUE"
        assert pawn.active
        assert (row, col) in (
            game.get_valid_moves()
            if game.selected_pawn is pawn
            else __get_moves(game, pawn)
        )


def test_legal_actions_only_contains_current_player():
    game = Game()

    game.dice.value = 1

    actions = game.get_legal_actions()

    for pawn, row, col in actions:
        assert pawn.team == game.current_player.team


def test_legal_actions_rejects_other_player():
    game = Game()

    game.dice.value = 1

    actions = game.get_legal_actions(game.red)

    assert actions == []


def test_legal_actions_empty_after_game_over():
    game = Game()

    game.dice.value = 1
    game.game_over = True

    actions = game.get_legal_actions()

    assert actions == []


def test_legal_actions_does_not_change_game_state():
    game = Game()

    game.dice.value = 3

    original_dice = game.dice.value
    original_player = game.current_player

    original_positions = [
        (pawn.id, pawn.row, pawn.col, pawn.active)
        for pawn in game.blue.pawns + game.red.pawns
    ]

    game.get_legal_actions()

    assert game.dice.value == original_dice
    assert game.current_player == original_player

    new_positions = [
        (pawn.id, pawn.row, pawn.col, pawn.active)
        for pawn in game.blue.pawns + game.red.pawns
    ]

    assert new_positions == original_positions


def __get_moves(game, pawn):
    from engine.movement import Movement

    return Movement.get_valid_moves_for_pawn(
        game,
        pawn
    )