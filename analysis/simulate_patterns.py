import argparse
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path


def targets_for(pattern):
    offset = (16 - pattern.size) // 2
    return {(r + offset, c + offset) for r, row in enumerate(pattern.grid)
            for c, cell in enumerate(row) if cell}


def choose_action(game, targets, rng, noise):
    actions = game.get_legal_actions()
    if not actions:
        return None
    team = game.current_player.team
    occupied = {(r, c) for r, c in targets
                if (p := game.board.get_pawn(r, c)) is not None and p.team == team}
    available = targets - occupied
    if not available:
        return rng.choice(actions)
    scored = []
    for pawn, r, c in actions:
        start = (pawn.row, pawn.col)
        before = min(max(abs(start[0] - t[0]), abs(start[1] - t[1])) for t in available)
        after = min(max(abs(r - t[0]), abs(c - t[1])) for t in available)
        capture = game.board.get_pawn(r, c) is not None
        # Prioritize exact placement, then progress and opponent disruption.
        score = (100 if (r, c) in available else 0) + (before - after) * 4 + (12 if capture else 0)
        # Moving a pawn away from an already occupied target is strongly discouraged.
        if start in occupied:
            score -= 110
        score += rng.random() * noise
        scored.append((score, pawn.id, pawn, r, c))
    _, _, pawn, row, col = max(scored, key=lambda item: item[0])
    return pawn, row, col


def run_one(pattern_path, seed, turns, noise):
    from engine.game import Game
    from engine.pattern import Pattern
    rng = random.Random(seed)
    game = Game()
    data = json.loads(pattern_path.read_text(encoding='utf-8'))
    game.pattern = Pattern()
    game.pattern.name = data['name']
    game.pattern.size = data['size']
    game.pattern.grid = data['grid']
    targets = targets_for(game.pattern)
    no_moves = 0
    for turn in range(1, turns + 1):
        # Seed only the dice call, preserving independent deterministic policy RNG.
        # Game uses module-level random for dice.
        game.dice.value = rng.randint(1, 6)
        game.turn_phase = game.WAITING_FOR_SELECTION
        action = choose_action(game, targets, rng, noise)
        if action is None:
            no_moves += 1
            game.switch_turn()
            continue
        pawn, row, col = action
        if not game.select_pawn(pawn.row, pawn.col):
            raise RuntimeError('Engine rejected selection')
        if not game.move_selected_pawn(row, col):
            raise RuntimeError('Engine rejected legal move')
        if game.game_over:
            return {'winner': game.winner.team, 'turns': turn, 'no_moves': no_moves,
                    'finished': True}
    return {'winner': '', 'turns': turns, 'no_moves': no_moves, 'finished': False}


def simulate(folder, games, turns, seed, noise):
    files = sorted(folder.glob('*.json'))
    if len(files) != 53:
        raise ValueError(f'Expected 53 patterns, found {len(files)} in {folder}')
    rows = []
    for i, path in enumerate(files):
        outcomes = [run_one(path, seed + i * 100000 + n, turns, noise) for n in range(games)]
        wins = Counter(o['winner'] for o in outcomes)
        finished = [o['turns'] for o in outcomes if o['finished']]
        rows.append({'pattern': path.stem, 'games': games, 'blue_wins': wins['BLUE'],
                     'red_wins': wins['RED'], 'timeouts': wins[''],
                     'completion_rate': round(len(finished) / games, 4),
                     'mean_win_turns': round(sum(finished)/len(finished), 1) if finished else '',
                     'no_legal_moves': sum(o['no_moves'] for o in outcomes)})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--patterns', type=Path, default=Path('patterns'))
    parser.add_argument('--games', type=int, default=4)
    parser.add_argument('--turns', type=int, default=400)
    parser.add_argument('--seed', type=int, default=52)
    parser.add_argument('--noise', type=float, default=0.5)
    parser.add_argument('--output', type=Path, default=Path('simulation_results.csv'))
    args = parser.parse_args()
    if args.games < 1 or args.turns < 1 or args.noise < 0:
        parser.error('games and turns must be positive; noise cannot be negative')
    rows = simulate(args.patterns, args.games, args.turns, args.seed, args.noise)
    with args.output.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} patterns, {len(rows)*args.games} games, "
          f"{sum(r['blue_wins'] for r in rows)} BLUE wins, "
          f"{sum(r['red_wins'] for r in rows)} RED wins, "
          f"{sum(r['timeouts'] for r in rows)} timeouts; output: {args.output}")


if __name__ == '__main__':
    main()
