"""Run after copying patterns/ into the Creator project."""
import json
from pathlib import Path

PATTERNS = Path(__file__).resolve().parents[1] / "patterns"


def test_full_pattern_library():
    files = sorted(PATTERNS.glob("*.json"))
    assert len(files) == 53
    names = set()
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["name"] not in names
        names.add(data["name"])
        assert data["size"] == 7
        assert len(data["grid"]) == 7
        assert all(len(row) == 7 for row in data["grid"])
        assert all(cell in (0, 1) for row in data["grid"] for cell in row)
        assert 5 <= sum(sum(row) for row in data["grid"]) <= 32
    assert set("ABCDEFGHIJKLMNOPQRSTUVWXYZ").issubset(names)
    assert set("123456789").issubset(names)
