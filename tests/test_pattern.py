from engine.pattern import Pattern


def test_pattern_defaults_before_loading():
    pattern = Pattern()

    assert pattern.name == ""
    assert pattern.size == 7
    assert pattern.grid == []


def test_load_random_sets_name_and_grid():
    pattern = Pattern()
    pattern.load_random()

    assert pattern.name != ""
    assert pattern.size > 0
    assert len(pattern.grid) == pattern.size


def test_load_random_grid_is_square_and_matches_size():
    pattern = Pattern()
    pattern.load_random()

    # Every row must have exactly `size` columns.
    for row in pattern.grid:
        assert len(row) == pattern.size


def test_load_random_grid_values_are_binary():
    pattern = Pattern()
    pattern.load_random()

    for row in pattern.grid:
        for cell in row:
            assert cell in (0, 1)


def test_load_random_can_pick_any_available_pattern_file():
    # Loading repeatedly should never raise and should always come back
    # with a valid pattern, regardless of which file random.choice picks.
    for _ in range(10):
        pattern = Pattern()
        pattern.load_random()

        assert pattern.name != ""
        assert len(pattern.grid) == pattern.size
