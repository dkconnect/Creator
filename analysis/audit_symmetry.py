"""Diagnose team symmetry and initial target-distance bias; no rule changes."""
import csv,json
from pathlib import Path
from engine.game import Game
from engine.pattern import Pattern
from analysis.simulate_progress import targets_for

def game_for(path,flip=False):
    game=Game()
    data=json.loads(path.read_text(encoding='utf-8'))
    game.pattern=Pattern();game.pattern.name=data['name'];game.pattern.size=data['size']
    game.pattern.grid=data['grid'][::-1] if flip else data['grid']
    return game

def metric(path):
    game=game_for(path); targets=targets_for(game.pattern)
    def nearest(team):
        pawns=game.blue.pawns if team=='BLUE' else game.red.pawns
        return sum(min(max(abs(p.row-r),abs(p.col-c)) for p in pawns) for r,c in targets)/len(targets)
    blue,red=nearest('BLUE'),nearest('RED')
    return {'pattern':path.stem,'targets':len(targets),'mean_target_row':round(sum(r for r,c in targets)/len(targets),3), 'blue_distance':round(blue,3),'red_distance':round(red,3),'red_minus_blue_distance':round(red-blue,3)}

def symmetric_legal_moves(path,die):
    a=game_for(path);a.dice.value=die;a.turn_phase=a.WAITING_FOR_SELECTION
    blue={(p.row,p.col,r,c) for p,r,c in a.get_legal_actions()}
    b=game_for(path);b.dice.value=die;b.turn_phase=b.WAITING_FOR_SELECTION;b.current_player=b.red
    red={(15-p.row,p.col,15-r,c) for p,r,c in b.get_legal_actions()}
    return blue==red

def main():
    paths=sorted(Path('patterns').glob('*.json'));assert len(paths)==53
    rows=[metric(p) for p in paths]
    with open('pattern_symmetry.csv','w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
    n=sum(symmetric_legal_moves(p,d) for p in paths for d in range(1,7))
    print('Mirrored initial legal actions:',n,'of',len(paths)*6)
    for label,fn in [('BLUE advantage',lambda d:d>0.0001),('RED advantage',lambda d:d< -0.0001),('tie',lambda d:abs(d)<=0.0001)]:
        print(label,sum(fn(r['red_minus_blue_distance']) for r in rows))
    print('Mean RED minus BLUE target distance:',round(sum(r['red_minus_blue_distance'] for r in rows)/len(rows),3))
    print('Top BLUE favored:',[(r['pattern'],r['red_minus_blue_distance']) for r in sorted(rows,key=lambda r:-r['red_minus_blue_distance'])[:5]])
    print('Top RED favored:',[(r['pattern'],r['red_minus_blue_distance']) for r in sorted(rows,key=lambda r:r['red_minus_blue_distance'])[:5]])
if __name__=='__main__':main()
