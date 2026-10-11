"""Deterministic greedy-policy benchmark for Step 52K (not human win-rate estimate)."""
import csv
import json
import random
from pathlib import Path
from engine.game import Game
from engine.pattern import Pattern
from engine.victory import target_cells, progress


def choose_action(game, rng):
    actions = game.get_legal_actions()
    if not actions:
        return None
    team = game.current_player.team
    targets = set(target_cells(game, team))
    opponent = "RED" if team == "BLUE" else "BLUE"
    opponent_targets = set(target_cells(game, opponent))
    occupied = {p for p in targets if (pawn := game.board.get_pawn(*p)) is not None and pawn.team == team}
    available = targets - occupied
    if not available:
        return rng.choice(actions)
    def evaluate(action):
        pawn, r, c = action
        start = (pawn.row, pawn.col)
        before = min(max(abs(start[0]-tr), abs(start[1]-tc)) for tr,tc in available)
        after = min(max(abs(r-tr), abs(c-tc)) for tr,tc in available)
        victim = game.board.get_pawn(r,c)
        capture = victim is not None and victim.team != team
        return (100 if (r,c) in available else 0) + 4*(before-after) + (12 if capture else 0) + (35 if capture and (r,c) in opponent_targets else 0) - (110 if start in occupied else 0) + rng.random()*.5
    return max(actions, key=evaluate)


def run_one(path, seed, starter):
    rng = random.Random(seed)
    game = Game()
    data = json.loads(path.read_text(encoding='utf-8'))
    game.pattern = Pattern()
    game.pattern.name, game.pattern.size, game.pattern.grid = data['name'], data['size'], data['grid']
    if starter == 'RED':
        game.current_player = game.red
    for _ in range(400):
        if game.game_over:
            break
        game.dice.value = rng.randint(1,6)
        game.turn_phase = game.WAITING_FOR_SELECTION
        action = choose_action(game,rng)
        if action is None:
            game.switch_turn()
        else:
            pawn,r,c = action
            assert game.select_pawn(pawn.row,pawn.col)
            assert game.move_selected_pawn(r,c)
    blue,total = progress(game,'BLUE')
    red,_ = progress(game,'RED')
    return {'pattern':path.stem,'starter':starter,'winner':game.winner.team if game.winner else 'DRAW', 'reason':game.result_reason or 'INCOMPLETE','turns':game.turn_count,'blue_held':blue,'red_held':red,'targets':total}


def main():
    paths = sorted(Path('patterns').glob('*.json'))
    assert len(paths) == 53, f'Expected 53 patterns, got {len(paths)}'
    rows=[]
    for i,path in enumerate(paths):
        for j in range(4):
            rows.append(run_one(path,52+i*100000+j,'BLUE' if j%2==0 else 'RED'))
    with open('benchmark_52k_results.csv','w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    from collections import Counter
    print('games',len(rows),'winners',dict(Counter(r['winner'] for r in rows)),'reasons',dict(Counter(r['reason'] for r in rows)))
    print('formation',sum(r['reason']=='formation' for r in rows),'decided',sum(r['winner']!='DRAW' for r in rows))
if __name__=='__main__': main()
