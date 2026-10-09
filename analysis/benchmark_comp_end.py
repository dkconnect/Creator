"""Competitive endgame benchmark; does not modify Creator rules."""
import argparse,csv,json,random,sys
from pathlib import Path
from engine.game import Game
from engine.pattern import Pattern
import engine.victory as victory
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




def count_targets(game, targets, team):
    return sum(1 for r,c in targets if (p:=game.board.get_pawn(r,c)) is not None and p.team==team)

def run(path,seed,limit,decision_turn):
    rng=random.Random(seed);game=Game(); data=json.loads(path.read_text(encoding="utf-8"))
    game.pattern=Pattern();game.pattern.name=data['name'];game.pattern.size=data['size'];game.pattern.grid=data['grid']
    targets=targets_for(game.pattern)
    for t in range(1,limit+1):
        game.dice.value=rng.randint(1,6);game.turn_phase=game.WAITING_FOR_SELECTION
        action=choose_action(game,targets,rng,.5)
        if action is None:
            game.switch_turn()
        else:
            pawn,row,col=action
            assert game.select_pawn(pawn.row,pawn.col)
            assert game.move_selected_pawn(row,col)
        if game.game_over:
            return game.winner.team,t,"full_pattern",count_targets(game,targets,"BLUE"),count_targets(game,targets,"RED")
        if t>=decision_turn and (t==decision_turn or t==limit):
            blue=count_targets(game,targets,"BLUE")
            red=count_targets(game,targets,"RED")
            if blue!=red or t==limit:
                return ("BLUE" if blue>red else "RED" if red>blue else ""),t,("decision" if blue!=red else "tie"),blue,red
    return "",limit,"tie",count_targets(game,targets,"BLUE"),count_targets(game,targets,"RED")

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--games',type=int,default=4);ap.add_argument('--turns',type=int,default=400);ap.add_argument('--decision-turn',type=int,default=320);a=ap.parse_args()
    if not (1 <= a.decision_turn <= a.turns): ap.error('decision-turn must be between 1 and turns')
    rows=[]
    project_dir = Path(__file__).resolve().parent
    pattern_dir = project_dir / 'patterns'
    if not pattern_dir.is_dir():
        ap.error(f"Pattern folder not found: {pattern_dir}. Place this script in your creator_v root beside the patterns folder.")
    paths = sorted(pattern_dir.glob('*.json'))
    if not paths:
        ap.error(f"No JSON patterns found in {pattern_dir}")
    if len(paths) != 53:
        ap.error(f"Expected 53 pattern JSON files in {pattern_dir}, found {len(paths)}")
    for i,path in enumerate(paths):
        results=[run(path,52+i*100000+j,a.turns,a.decision_turn) for j in range(a.games)]
        rows.append(dict(pattern=path.stem,blue=sum(w=='BLUE' for w,*_ in results),red=sum(w=='RED' for w,*_ in results),ties=sum(not w for w,*_ in results),full_pattern=sum(kind=='full_pattern' for w,t,kind,b,r in results),decisions=sum(kind=='decision' for w,t,kind,b,r in results),mean_blue_occupied=round(sum(b for w,t,k,b,r in results)/len(results),2),mean_red_occupied=round(sum(r for w,t,k,b,r in results)/len(results),2)))
    target=project_dir / 'competitive_endgame_results.csv'
    with target.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    print('Patterns:',len(paths),'| Output:',target)
    print('games',len(rows)*a.games,'blue',sum(r['blue'] for r in rows),'red',sum(r['red'] for r in rows),'ties',sum(r['ties'] for r in rows),'full_pattern',sum(r['full_pattern'] for r in rows),'decisions',sum(r['decisions'] for r in rows))
if __name__=='__main__':main()
