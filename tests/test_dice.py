from engine.dice import Dice


def test_dice_value_is_none_before_rolling():
    dice = Dice()

    assert dice.value is None


def test_roll_returns_value_between_1_and_6():
    dice = Dice()

    for _ in range(50):
        value = dice.roll()

        assert 1 <= value <= 6
        assert dice.value == value
