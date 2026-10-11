# Creator — Seeded simulation benchmark

## Method

- 53 pattern JSON definitions, 4 games per pattern, 212 games total.
- Each game starts with Creator's real `Game` board and 32 pawns per team.
- Each turn uses a seeded uniform die roll (1–6) and the engine's legal action generator, selection, move execution, capture/respawn and victory checks.
- Both sides use the same *greedy target-seeking* policy: prefer filling missing target cells, approaching unfilled targets, and capturing enemies; avoid moving pawns off completed target cells.
- Maximum 400 **player turns** per game (not 400 full rounds). A timeout is not a draw adjudicated by Creator; it means the benchmark stopped.
- Seed: 52; strategy noise: 0.5. Repeating the same command produced a byte-identical CSV.

## Results

| Metric | Value |
|---|---:|
| Games | 212 |
| BLUE wins | 7 |
| RED wins | 1 |
| Timed out at 400 turns | 204 |
| Completion rate | 3.77% |

## Interpretation

Completion is rare with this simplistic policy and turn budget. This is a useful warning about benchmark difficulty, **not** proof of broken victory rules, unreachable patterns, or an intrinsic BLUE advantage. There were only eight wins, far too few for reliable side-balance inference. This benchmark is not the shipped Basic/Learning/Advanced AI, and its greedy decisions can trap it in local optima.

## Reproduce

Copy `simulate_patterns.py` into the Creator project root, then run:

```powershell
python simulate_patterns.py --patterns patterns --games 4 --turns 400 --seed 52 --output simulation_results.csv
```

For more stable rates, increase games and vary the seed; expect longer execution time. Future work should compare policy variants, longer turn limits and paired seeds with reversed team assignments before publishing difficulty labels.

## Project changes

None: no changes to engine, network protocol, UI or pattern JSON.
