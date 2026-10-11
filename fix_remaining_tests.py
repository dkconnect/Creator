from pathlib import Path
import re
import shutil

ROOT = Path.cwd()

def replace_function(path, function_name, replacement):
    source = path.read_text(encoding='utf-8')
    regex = rf'(?m)^def {re.escape(function_name)}\(\):\n.*?(?=^def test_|\Z)'
    result, count = re.subn(regex, lambda _: replacement.rstrip() + '\n\n', source, count=1, flags=re.S | re.M)
    if count != 1:
        raise RuntimeError(f'Cannot find exactly one {function_name} in {path}; no changes made')
    return result

victory_path = ROOT / 'tests' / 'test_victory.py'
advanced_path = ROOT / 'tests' / 'test_advanced_ai.py'
for p in (victory_path, advanced_path):
    if not p.is_file():
        raise SystemExit(f'Missing {p}. Run from the creator_v root directory.')

victory = victory_path.read_text(encoding='utf-8')
for name, body in [
    ('test_victory_false_when_a_required_cell_is_empty', '''def test_victory_false_when_a_required_cell_is_empty():
    game = Game()
    game.pattern = make_pattern(SIMPLE_GRID)
    fill_pattern_for_team(game, "BLUE")
    offset = centered_offset(game)
    # With 4 cells, 3 occupied is a win; 2 occupied is not.
    game.board.grid[offset][offset] = None
    assert victory.check_victory(game, game.blue) is True
    game.board.grid[offset][offset + 1] = None
    assert victory.check_victory(game, game.blue) is False
'''),
    ('test_victory_false_when_a_required_cell_belongs_to_opponent', '''def test_victory_false_when_a_required_cell_belongs_to_opponent():
    game = Game()
    game.pattern = make_pattern(SIMPLE_GRID)
    fill_pattern_for_team(game, "BLUE")
    offset = centered_offset(game)
    # An opponent on one of four cells leaves exactly 75% for BLUE.
    game.board.grid[offset][offset] = Pawn(
        id=8000, team="RED", row=offset, col=offset
    )
    assert victory.check_victory(game, game.blue) is True
    game.board.grid[offset][offset + 1] = Pawn(
        id=8001, team="RED", row=offset, col=offset + 1
    )
    assert victory.check_victory(game, game.blue) is False
'''),
]:
    regex = rf'(?m)^def {name}\(\):\n.*?(?=^def test_|\Z)'
    victory, count = re.subn(regex, lambda _: body.rstrip() + '\n\n', victory, count=1, flags=re.S | re.M)
    if count != 1:
        raise SystemExit(f'Could not locate {name}; no files changed')

advanced = advanced_path.read_text(encoding='utf-8')
name = 'test_advanced_ai_takes_immediate_win'
body = '''def test_advanced_ai_takes_immediate_win():
    game = Game()
    game.pattern = make_test_pattern([[1]])
    from engine.victory import target_cells
    target = target_cells(game, "RED")[0]
    ai = AdvancedAI(team="RED")

    # RED's target is mirrored vertically, so it is (8, 7), not (7, 7).
    # Position a pawn exactly 3 steps below the target.
    pawn = game.red.pawns[0]
    game.board.grid[pawn.row][pawn.col] = None
    pawn.row, pawn.col = target[0] + 3, target[1]
    game.board.place_pawn(pawn)

    game.dice.value = 3
    action = ai.select_move(game)
    assert action is not None
    chosen_pawn, tr, tc = action
    assert chosen_pawn is pawn
    assert (tr, tc) == target
'''
regex = rf'(?m)^def {name}\(\):\n.*?(?=^def test_|\Z)'
advanced, count = re.subn(regex, lambda _: body.rstrip() + '\n\n', advanced, count=1, flags=re.S | re.M)
if count != 1:
    raise SystemExit(f'Could not locate {name}; no files changed')

for p, content in ((victory_path, victory), (advanced_path, advanced)):
    shutil.copy2(p, p.with_suffix(p.suffix + '.bak'))
    p.write_text(content, encoding='utf-8')
    print(f'Updated {p.relative_to(ROOT)} (backup: {p.name}.bak)')
print('Run: python -m pytest -q')
