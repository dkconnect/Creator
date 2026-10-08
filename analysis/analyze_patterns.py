"""Creator Step 52B: deterministic pattern geometry audit (standard library only).

Run: python analyze_patterns.py PATH_TO_CREATOR/patterns
Produces pattern_balance.csv and PATTERN_BALANCE_REPORT.md beside this script.
Metrics are heuristics, not measured win rates or proof of solvability.
"""
import csv
import json
import sys
from collections import deque
from pathlib import Path

BOARD = 16
DIRECTIONS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]


def distance_map(start_rows):
    """Minimum dice moves on an empty board, any roll 1..6 (not expected turns)."""
    dist = {(r, c): 0 for r in start_rows for c in range(BOARD)}
    queue = deque(dist)
    while queue:
        r, c = queue.popleft()
        for dr, dc in DIRECTIONS:
            for roll in range(1, 7):
                point = (r + dr * roll, c + dc * roll)
                if 0 <= point[0] < BOARD and 0 <= point[1] < BOARD and point not in dist:
                    dist[point] = dist[(r, c)] + 1
                    queue.append(point)
    return dist


def analyze(folder):
    blue = distance_map((0, 1))
    red = distance_map((14, 15))
    results = []
    for path in sorted(folder.glob('*.json')):
        obj = json.loads(path.read_text(encoding='utf-8'))
        size, grid = obj['size'], obj['grid']
        if size != 7 or len(grid) != size or any(len(row) != size for row in grid):
            raise ValueError(f'Unexpected grid geometry: {path}')
        offset = (BOARD - size) // 2
        targets = {(r + offset, c + offset) for r in range(size)
                   for c in range(size) if grid[r][c] == 1}
        if not targets or len(targets) > 32:
            raise ValueError(f'Invalid pawn requirement: {path}')
        adjacency = sum((r + dr, c + dc) in targets
                        for r, c in targets for dr, dc in ((1, 0), (0, 1)))
        sides = []
        for label, distances in [('BLUE', blue), ('RED', red)]:
            values = [distances[cell] for cell in targets]
            sides.append((label, sum(values), max(values)))
        n = len(targets)
        # Difficulty index is an *editorial* ordering proxy. The pawn count
        # dominates; route distance and local density break ties.
        score = round(n * 4 + max(s[1] for s in sides) / n * 3 + adjacency * 0.5, 2)
        results.append(dict(file=path.name, category=path.stem.split('_')[0],
                            pattern=obj['name'], pawns=n, adjacent_pairs=adjacency,
                            blue_min_move_sum=sides[0][1], red_min_move_sum=sides[1][1],
                            blue_max_min_moves=sides[0][2], red_max_min_moves=sides[1][2],
                            balance_gap=abs(sides[0][1] - sides[1][1]),
                            heuristic_score=score))
    ranked = sorted(results, key=lambda r: (r['heuristic_score'], r['file']))
    for rank, item in enumerate(ranked, 1):
        item['rank'] = rank
        item['tier'] = ('Starter' if rank <= 13 else 'Intermediate' if rank <= 27
                        else 'Challenging' if rank <= 40 else 'Expert')
    return results


def write_outputs(results, output):
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'pattern_balance.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(sorted(results, key=lambda x: x['rank']))
    ordered = sorted(results, key=lambda x: x['rank'])
    lines = ['# Creator — Pattern Balance Audit', '',
             '## Method and limitations', '',
             '- All patterns are centered at `(16 − 7) // 2 = 4`, matching the victory engine.',
             '- `pawns`: number of required occupied cells, out of 32 available pawns per team.',
             '- `adjacent_pairs`: horizontally/vertically touching required cells; a density proxy, **not** a collision simulation.',
             '- `*_min_move_sum`: sum of minimum number of legal-distance moves from either starting row to each target on an **empty board**, assuming favorable dice outcomes. Pawns, obstacles, captures, and roll probabilities are excluded.',
             '- `balance_gap`: absolute difference in those BLUE/RED optimistic sums; it is **not** an estimated win-rate difference.',
             '- `heuristic_score = 4 × pawns + 3 × (larger minimum-move sum / pawns) + 0.5 × adjacent_pairs`.',
             '- Tiers are relative quartiles of this score, **not** measured difficulty or predicted match length.',
             '- No game rules or JSON definitions are modified.', '',
             '## Summary', '',
             f'- Patterns: **{len(results)}**',
             f'- Required pawn range: **{min(r["pawns"] for r in results)}–{max(r["pawns"] for r in results)}**',
             f'- Patterns with unequal BLUE/RED optimistic travel sums: **{sum(r["balance_gap"] > 0 for r in results)}**', '',
             '## Ranked patterns', '',
             '| Rank | Pattern | Pawns | Adjacent pairs | BLUE sum | RED sum | Gap | Tier |',
             '|---:|---|---:|---:|---:|---:|---:|---|']
    for r in ordered:
        lines.append(f'| {r["rank"]} | {r["pattern"]} (`{r["file"]}`) | {r["pawns"]} | {r["adjacent_pairs"]} | {r["blue_min_move_sum"]} | {r["red_min_move_sum"]} | {r["balance_gap"]} | {r["tier"]} |')
    lines += ['', '## Next validation stage', '',
              'Run seeded, full-match simulations with representative policies and dice rolls, record win rates and turn counts by pattern/team, and only then decide whether to revise the difficulty labels or templates.',
              'The current audit does **not** establish strategic reachability or fair win rates.']
    (output / 'PATTERN_BALANCE_REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('patterns')
    if not folder.is_dir():
        raise SystemExit(f'Pattern folder not found: {folder}')
    rows = analyze(folder)
    if len(rows) != 53:
        raise SystemExit(f'Expected 53 patterns, found {len(rows)}')
    write_outputs(rows, Path(__file__).resolve().parent)
    print(f'Analyzed {len(rows)} patterns; files written beside script')
    print('Easiest proxy:', [(r['pattern'], r['pawns']) for r in sorted(rows, key=lambda r:r['rank'])[:5]])
    print('Hardest proxy:', [(r['pattern'], r['pawns']) for r in sorted(rows, key=lambda r:r['rank'])[-5:]])
