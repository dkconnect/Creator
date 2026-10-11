import argparse
import csv
import itertools
import json
import random
from pathlib import Path

from engine.game import Game
from engine.pattern import Pattern
from engine.victory import progress
from engine.ai.basic_ai import BasicAI
from engine.ai.learning_ai import LearningAI
from engine.ai.advanced_ai import AdvancedAI

AGENTS = {'basic': BasicAI, 'learning': LearningAI, 'advanced': AdvancedAI}


def play_game(pattern_path, blue_agent, red_agent, seed, starter, turns):
    dice_rng = random.Random(seed)
    random.seed(seed ^ 0x5A17)
    game = Game()
    data = json.loads(Path(pattern_path).read_text(encoding='utf-8'))
    game.pattern = Pattern()
    game.pattern.name, game.pattern.size, game.pattern.grid = data['name'], data['size'], data['grid']
    agents = {'BLUE': AGENTS[blue_agent]('BLUE'), 'RED': AGENTS[red_agent]('RED')}
    game.current_player = game.blue if starter == 'BLUE' else game.red
    peak = {'BLUE': 0, 'RED': 0}
    peak_turn = {'BLUE': 0, 'RED': 0}
    dice_sequence = []
    for turn in range(turns + 1):
        for team in ('BLUE', 'RED'):
            held, _ = progress(game, team)
            if held > peak[team]:
                peak[team], peak_turn[team] = held, turn
        if game.game_over or turn == turns:
            break
        roll = dice_rng.randint(1, 6)
        dice_sequence.append(roll)
        game.dice.value = roll
        game.turn_phase = game.WAITING_FOR_SELECTION
        player_team = game.current_player.team
        action = agents[player_team].select_move(game)
        if action is None:
            game.switch_turn()
            continue
        pawn, row, col = action
        from_pos = (pawn.row, pawn.col)
        destination_pawn = game.board.get_pawn(row, col)
        was_capture = destination_pawn is not None and destination_pawn.team != player_team
        if pawn.team != player_team or not game.select_pawn(pawn.row, pawn.col) or not game.move_selected_pawn(row, col):
            raise RuntimeError(f'{player_team} {agents[player_team].__class__.__name__} returned illegal action at turn {turn}')

        opponent = 'RED' if player_team == 'BLUE' else 'BLUE'
        if isinstance(agents[opponent], LearningAI):
            agents[opponent].record_human_move(game, from_pos, (row, col), was_capture)
    blue_held, total = progress(game, 'BLUE')
    red_held, _ = progress(game, 'RED')

    return {
        'pattern': Path(pattern_path).stem, 'seed': seed, 'starter': starter,
        'blue_agent': blue_agent, 'red_agent': red_agent,
        'status': 'WIN' if game.winner else 'UNFINISHED',
        'winner': game.winner.team if game.winner else '',
        'turns_played': turn, 'target_cells': total,
        'blue_held': blue_held, 'red_held': red_held,
        'blue_peak': peak['BLUE'], 'red_peak': peak['RED'],
        'blue_peak_pct': round(100 * peak['BLUE'] / total, 2) if total else 0,
        'red_peak_pct': round(100 * peak['RED'] / total, 2) if total else 0,
        'blue_peak_turn': peak_turn['BLUE'], 'red_peak_turn': peak_turn['RED'],
        'blue_captures_suffered': game.blue.captures_suffered,
        'red_captures_suffered': game.red.captures_suffered,
        'dice_sequence': '-'.join(map(str, dice_sequence)),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agents', nargs='+', choices=sorted(AGENTS), default=['basic', 'learning'])
    parser.add_argument('--turns', type=int, default=400)
    parser.add_argument('--games-per-pattern', type=int, default=2)
    parser.add_argument('--seed', type=int, default=57)
    parser.add_argument('--patterns', type=Path, default=Path('patterns'))
    parser.add_argument('--output', type=Path, default=Path('analysis/benchmark_step57.csv'))
    args = parser.parse_args(argv)
    if args.turns < 1 or args.games_per_pattern < 2 or args.games_per_pattern % 2:
        parser.error('--turns must be positive and --games-per-pattern must be a positive even number')
    paths = sorted(args.patterns.glob('*.json'))
    if not paths:
        parser.error('No pattern JSON files found')
        
    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = wins = 0
    with args.output.open('w', newline='', encoding='utf-8') as out:
        writer = None
        
        for i, path in enumerate(paths):
            for blue, red in itertools.product(args.agents, repeat=2):
                for j in range(0, args.games_per_pattern, 2):
                    seed = args.seed + i * 100003 + j // 2
                    for starter in ('BLUE', 'RED'):
                        row = play_game(path, blue, red, seed, starter, args.turns)
                        if writer is None:
                            writer = csv.DictWriter(out, fieldnames=list(row))
                            writer.writeheader()
                        writer.writerow(row)
                        count += 1
                        wins += row['status'] == 'WIN'
    print(f'{count} games; {wins} full-formation wins; {count-wins} unfinished at benchmark horizon')
    print(f'CSV: {args.output}')
    print('Unfinished is not a draw or occupancy win. Dice sequences are paired by seed and starter.')


if __name__ == '__main__':
    main()
