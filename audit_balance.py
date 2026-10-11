"""Step 52L: analyze existing benchmark, without modifying Creator gameplay.
Run: python audit_balance.py --results benchmark_52k_results.csv --patterns patterns
"""
import argparse,csv,json,collections,statistics
from pathlib import Path

def targets(data,team):
    off=(16-data['size'])//2
    cells=[(r+off,c+off) for r,row in enumerate(data['grid']) for c,x in enumerate(row) if x==1]
    return cells if team=='BLUE' else [(15-r,c) for r,c in cells]

def distance(team,cells):
    starts=[(r,c) for r in ((0,1) if team=='BLUE' else (14,15)) for c in range(16)]
    return sum(min(max(abs(r-pr),abs(c-pc)) for pr,pc in starts) for r,c in cells)/len(cells)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);ap.add_argument('--patterns',type=Path,required=True);args=ap.parse_args()
    rows=list(csv.DictReader(args.results.open(newline='',encoding='utf-8')))
    by_starter=collections.defaultdict(collections.Counter)
    by_reason=collections.defaultdict(collections.Counter)
    by_pattern=collections.defaultdict(collections.Counter)
    for row in rows:
        by_starter[row['starter']][row['winner']]+=1
        by_reason[row['reason']][row['winner']]+=1
        by_pattern[row['pattern']][row['winner']]+=1
    print('Games:',len(rows))
    print('By starter:',{k:dict(v) for k,v in sorted(by_starter.items())})
    print('By reason:',{k:dict(v) for k,v in sorted(by_reason.items())})
    gaps=[];overlaps=[];missing=[]
    for stem in sorted(by_pattern):
        path=args.patterns/(stem+'.json')
        if not path.exists():missing.append(stem);continue
        data=json.loads(path.read_text(encoding='utf-8'))
        blue=targets(data,'BLUE');red=targets(data,'RED')
        gaps.append((stem,distance('BLUE',blue)-distance('RED',red)))
        overlaps.append((stem,len(set(blue)&set(red)),len(blue)))
    if gaps:
        print('Mirrored initial distance gap (BLUE - RED): mean',round(statistics.mean(v for _,v in gaps),5),'max absolute',round(max(abs(v) for _,v in gaps),5))
        print('Nonzero geometry gaps:',[(k,round(v,4)) for k,v in gaps if abs(v)>1e-9][:10])
    if overlaps:
        print('Overlapping team target cells:',sum(x for _,x,_ in overlaps),'across',sum(x>0 for _,x,_ in overlaps),'patterns')
    if missing:print('Missing pattern JSON:',missing)
    print('Patterns favoring RED:',sum(v['RED']>v['BLUE'] for v in by_pattern.values()),'BLUE:',sum(v['BLUE']>v['RED'] for v in by_pattern.values()),'equal:',sum(v['BLUE']==v['RED'] for v in by_pattern.values()))
    print('NOTE: Greedy-policy simulation is not a human/AI 50-50 fairness measurement.')
if __name__=='__main__':main()
