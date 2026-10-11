import argparse
import csv
import json
import random
from pathlib import Path

from engine.game import Game
from engine.pattern import Pattern
from engine.victory import progress, target_cells


def choose_action(game, rng):
    actions = game.get_legal_actions()
    if not actions:
        return None
    team = game.current_player.team
    targets = set(target_cells(game, team))
    held = {pos for pos in targets if (p := game.board.get_pawn(*pos)) is not None and p.team == team}
    missing = targets - held
    if not missing:
        return rng.choice(actions)

    def score(action):
        pawn, row, col = action
        start = (pawn.row, pawn.col)
        before = min(max(abs(start[0] - r), abs(start[1] - c)) for r, c in missing)
        after = min(max(abs(row - r), abs(col - c)) for r, c in missing)
        enemy = game.board.get_pawn(row, col)
        capture = enemy is not None and enemy.team != team
        return (100 if (row, col) in missing else 0) + 4 * (before - after) + (12 if capture else 0) - (110 if start in held else 0) + rng.random() * .5

    return max(actions, key=score)


def run_game(pattern_path, seed, starter, max_turns):
    rng = random.Random(seed)
    game = Game()
    data = json.loads(pattern_path.read_text(encoding='utf-8'))
    game.pattern = Pattern()
    game.pattern.name = data['name']
    game.pattern.size = data['size']
    game.pattern.grid = data['grid']
    game.current_player = game.blue if starter == 'BLUE' else game.red
    peak = {'BLUE': 0, 'RED': 0}
    peak_turn = {'BLUE': 0, 'RED': 0}
    for turn in range(max_turns + 1):
        for team in ('BLUE', 'RED'):
            held, _ = progress(game, team)
            if held > peak[team]:
                peak[team] = held
                peak_turn[team] = turn
        if game.game_over or turn == max_turns:
            break
        game.dice.value = rng.randint(1, 6)
        game.turn_phase = game.WAITING_FOR_SELECTION
        action = choose_action(game, rng)
        if action is None:
            game.switch_turn()
        else:
            pawn, r, c = action
            if not game.select_pawn(pawn.row, pawn.col) or not game.move_selected_pawn(r, c):
                raise RuntimeError('Benchmark selected an illegal action')
    blue, total = progress(game, 'BLUE')
    red, _ = progress(game, 'RED')
    return dict(pattern=pattern_path.stem, seed=seed, starter=starter,
                status='WIN' if game.game_over and game.winner else 'UNFINISHED',
                winner=game.winner.team if game.winner else '',
                turns_played=turn + (0 if game.game_over else 0),
                target_cells=total, blue_held=blue, red_held=red,
                blue_peak=peak['BLUE'], red_peak=peak['RED'],
                blue_peak_pct=round(100 * peak['BLUE'] / total, 2) if total else 0,
                red_peak_pct=round(100 * peak['RED'] / total, 2) if total else 0,
                blue_peak_turn=peak_turn['BLUE'], red_peak_turn=peak_turn['RED'],
                blue_captures_suffered=game.blue.captures_suffered,
                red_captures_suffered=game.red.captures_suffered)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--turns', type=int, default=400)
    parser.add_argument('--games-per-pattern', type=int, default=2)
    parser.add_argument('--seed', type=int, default=54)
    parser.add_argument('--patterns', type=Path, default=Path('patterns'))
    parser.add_argument('--output', type=Path, default=Path('analysis/benchmark_step55.csv'))
    args = parser.parse_args()
    if args.turns < 1 or args.games_per_pattern < 1:
        parser.error('turns and games-per-pattern must be positive')
    paths = sorted(args.patterns.glob('*.json'))
    if not paths:
        parser.error('No pattern JSON files found')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = wins = 0
    with args.output.open('w', newline='', encoding='utf-8') as out:
        writer = None
        for i, path in enumerate(paths):
            for j in range(args.games_per_pattern):
                # Consecutive BLUE/RED starter runs share a random seed.
                row = run_game(path, args.seed + i * 100003 + j // 2, 'BLUE' if j % 2 == 0 else 'RED', args.turns)
                if writer is None:
                    writer = csv.DictWriter(out, fieldnames=list(row))
                    writer.writeheader()
                writer.writerow(row)
                count += 1
                wins += row['status'] == 'WIN'
    print(f'{count} games; {wins} full-formation wins; {count-wins} unfinished at benchmark horizon')
    print(f'CSV: {args.output}')
    print('Benchmark horizon does not end real matches or award occupancy wins.')


if __name__ == '__main__':
    main()
