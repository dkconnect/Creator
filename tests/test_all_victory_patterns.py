import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from engine.board import Board
from engine.pawn import Pawn
from engine.victory import check_victory


PATTERNS = Path(__file__).resolve().parents[1] / "patterns"
FILES = sorted(PATTERNS.glob("*.json"))


def _build(path, team="BLUE"):
    data = json.loads(path.read_text(encoding="utf-8"))
    pattern = SimpleNamespace(**data)
    board = Board()
    offset = (board.size - pattern.size) // 2
    cells = [(r + offset, c + offset)
             for r, row in enumerate(pattern.grid)
             for c, value in enumerate(row) if value == 1]
    for pawn_id, (r, c) in enumerate(cells):
        board.place_pawn(Pawn(id=pawn_id, team=team, row=r, col=c))
    game = SimpleNamespace(board=board, pattern=pattern)
    return game, cells


def test_catalog_has_exactly_53_unique_patterns():
    assert len(FILES) == 53
    names = [json.loads(path.read_text(encoding="utf-8"))["name"] for path in FILES]
    assert len(set(names)) == 53


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.stem)
def test_pattern_geometry(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    size = data["size"]
    grid = data["grid"]
    assert isinstance(size, int) and 1 <= size <= 16
    assert len(grid) == size
    assert all(len(row) == size and all(cell in (0, 1) for cell in row)
               for row in grid)
    assert 1 <= sum(sum(row) for row in grid) <= 32
    assert any(any(row) for row in grid)


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.stem)
@pytest.mark.parametrize("team", ["BLUE", "RED"])
def test_full_pattern_wins_for_its_team_only(path, team):
    game, _ = _build(path, team)
    assert check_victory(game, SimpleNamespace(team=team))
    other = "RED" if team == "BLUE" else "BLUE"
    assert not check_victory(game, SimpleNamespace(team=other))


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.stem)
@pytest.mark.parametrize("team", ["BLUE", "RED"])
def test_one_missing_target_prevents_victory(path, team):
    game, cells = _build(path, team)
    r, c = cells[len(cells)//2]
    game.board.grid[r][c] = None
    assert not check_victory(game, SimpleNamespace(team=team))


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.stem)
@pytest.mark.parametrize("team", ["BLUE", "RED"])
def test_one_enemy_on_target_prevents_victory(path, team):
    game, cells = _build(path, team)
    r, c = cells[len(cells)//2]
    enemy = "RED" if team == "BLUE" else "BLUE"
    game.board.place_pawn(Pawn(id=99, team=enemy, row=r, col=c))
    assert not check_victory(game, SimpleNamespace(team=team))


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.stem)
def test_extra_friendly_pawn_outside_pattern_is_allowed(path):
    game, cells = _build(path)
    free = next((r, c) for r in range(16) for c in range(16)
                if (r, c) not in cells)
    game.board.place_pawn(Pawn(id=99, team="BLUE", row=free[0], col=free[1]))
    assert check_victory(game, SimpleNamespace(team="BLUE"))
