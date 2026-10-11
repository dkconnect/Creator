# Symmetry and Starting-Position Audit

## Setup

- Source: 53 existing JSON victory patterns and Creator's current movement engine.
- Both teams retain their standard starting positions (BLUE rows 0–1; RED rows 14–15).
- Each required pattern cell is mapped onto the 16×16 board using the existing centering formula.
- For each cell, the distance to the nearest starting pawn of each team is calculated using Chebyshev distance (the optimistic number of king-like steps, *not* dice-roll moves).
- The per-pattern metric is the average of those distances over required cells.
- A separate test compares the set of legal BLUE moves with the vertically mirrored legal RED moves for every pattern and dice value 1–6 at game start.

## Results

- Initial legal-move symmetry: **318/318 mirrored comparisons matched**.
- Initial nearest-pawn target distance: **51 patterns favor BLUE, 2 favor RED**.
- Mean RED minus BLUE target distance: **+1.197 squares** across the 53 patterns.
- Largest BLUE-favoring differences: QUESTION +3.222, T +3.182, 7 +3.182, T_SHAPE +2.778, F +2.714.
- RED-favoring differences: L -1.182, L_SHAPE -0.778.

## Interpretation

This supports a **starting-distance asymmetry** in the current fixed-orientation pattern set. It does not prove a win-rate advantage of a particular size. The prior simulation's greedy strategy and its dice sequences may amplify this asymmetry. The legal-move symmetry result only verifies the *initial position*, not all reachable game states.

## Recommendations

1. **Do not change the movement or respawn rules** based on this diagnostic.
2. Run a paired experiment in which every pattern is also vertically reflected, using identical seed sets and both starting-player orders. Compare BLUE and RED progress and wins.
3. If the bias persists in human play, consider a match-level option that randomly chooses the vertical pattern orientation, synchronized for both Friend Room players. This avoids altering the 53 pattern definitions.
4. Keep difficulty ratings provisional until paired mirrored trials and stronger strategies have been evaluated.

## Reproduce

From the Creator project root, place `audit_symmetry.py` beside `main.py`, then run:

```sh
python audit_symmetry.py
```

The script writes `pattern_symmetry.csv`. It does not modify game files.
