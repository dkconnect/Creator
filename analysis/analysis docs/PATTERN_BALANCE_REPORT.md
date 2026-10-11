# Creator — Pattern Balance Audit

## Method and limitations

- All patterns are centered at `(16 − 7) // 2 = 4`, matching the victory engine.
- `pawns`: number of required occupied cells, out of 32 available pawns per team.
- `adjacent_pairs`: horizontally/vertically touching required cells; a density proxy, **not** a collision simulation.
- `*_min_move_sum`: sum of minimum number of legal-distance moves from either starting row to each target on an **empty board**, assuming favorable dice outcomes. Pawns, obstacles, captures, and roll probabilities are excluded.
- `balance_gap`: absolute difference in those BLUE/RED optimistic sums; it is **not** an estimated win-rate difference.
- `heuristic_score = 4 × pawns + 3 × (larger minimum-move sum / pawns) + 0.5 × adjacent_pairs`.
- Tiers are relative quartiles of this score, **not** measured difficulty or predicted match length.
- No game rules or JSON definitions are modified.

## Summary

- Patterns: **53**
- Required pawn range: **5–21**
- Patterns with unequal BLUE/RED optimistic travel sums: **47**

## Ranked patterns

| Rank | Pattern | Pawns | Adjacent pairs | BLUE sum | RED sum | Gap | Tier |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | DIAGONAL (`shape_DIAGONAL.json`) | 5 | 0 | 7 | 8 | 1 | Starter |
| 2 | LINE (`shape_LINE.json`) | 5 | 4 | 5 | 10 | 5 | Starter |
| 3 | EXCLAMATION (`symbol_EXCLAMATION.json`) | 6 | 4 | 8 | 10 | 2 | Starter |
| 4 | DIAMOND (`shape_DIAMOND.json`) | 8 | 0 | 11 | 13 | 2 | Starter |
| 5 | ZIGZAG (`shape_ZIGZAG.json`) | 8 | 7 | 10 | 14 | 4 | Starter |
| 6 | QUESTION (`symbol_QUESTION.json`) | 9 | 3 | 11 | 16 | 5 | Starter |
| 7 | L_SHAPE (`shape_L_SHAPE.json`) | 9 | 8 | 15 | 12 | 3 | Starter |
| 8 | CROSS (`shape_CROSS.json`) | 9 | 8 | 11 | 16 | 5 | Starter |
| 9 | T_SHAPE (`shape_T_SHAPE.json`) | 9 | 8 | 11 | 16 | 5 | Starter |
| 10 | TRIANGLE (`shape_TRIANGLE.json`) | 10 | 6 | 15 | 15 | 0 | Starter |
| 11 | Y (`letter_Y.json`) | 10 | 5 | 13 | 17 | 4 | Starter |
| 12 | 1 (`number_1.json`) | 10 | 9 | 15 | 15 | 0 | Starter |
| 13 | TIMES (`symbol_TIMES.json`) | 11 | 2 | 16 | 17 | 1 | Starter |
| 14 | 7 (`number_7.json`) | 11 | 7 | 14 | 19 | 5 | Intermediate |
| 15 | L (`letter_L.json`) | 11 | 10 | 18 | 15 | 3 | Intermediate |
| 16 | T (`letter_T.json`) | 11 | 10 | 14 | 19 | 5 | Intermediate |
| 17 | PLUS (`symbol_PLUS.json`) | 11 | 10 | 14 | 19 | 5 | Intermediate |
| 18 | J (`letter_J.json`) | 12 | 9 | 18 | 18 | 0 | Intermediate |
| 19 | X (`letter_X.json`) | 13 | 4 | 19 | 20 | 1 | Intermediate |
| 20 | RECTANGLE (`shape_RECTANGLE.json`) | 12 | 12 | 17 | 19 | 2 | Intermediate |
| 21 | V (`letter_V.json`) | 13 | 8 | 18 | 21 | 3 | Intermediate |
| 22 | C (`letter_C.json`) | 13 | 10 | 19 | 20 | 1 | Intermediate |
| 23 | K (`letter_K.json`) | 14 | 7 | 20 | 22 | 2 | Intermediate |
| 24 | 2 (`number_2.json`) | 14 | 8 | 21 | 21 | 0 | Intermediate |
| 25 | 4 (`number_4.json`) | 14 | 12 | 21 | 21 | 0 | Intermediate |
| 26 | F (`letter_F.json`) | 14 | 13 | 17 | 25 | 8 | Intermediate |
| 27 | Z (`letter_Z.json`) | 15 | 10 | 22 | 23 | 1 | Intermediate |
| 28 | S (`letter_S.json`) | 15 | 10 | 21 | 24 | 3 | Challenging |
| 29 | 3 (`number_3.json`) | 15 | 10 | 21 | 24 | 3 | Challenging |
| 30 | U (`letter_U.json`) | 15 | 12 | 22 | 23 | 1 | Challenging |
| 31 | I (`letter_I.json`) | 15 | 14 | 22 | 23 | 1 | Challenging |
| 32 | P (`letter_P.json`) | 15 | 13 | 18 | 27 | 9 | Challenging |
| 33 | O (`letter_O.json`) | 16 | 12 | 23 | 25 | 2 | Challenging |
| 34 | SQUARE (`shape_SQUARE.json`) | 16 | 16 | 23 | 25 | 2 | Challenging |
| 35 | Q (`letter_Q.json`) | 17 | 10 | 25 | 26 | 1 | Challenging |
| 36 | 8 (`number_8.json`) | 17 | 10 | 24 | 27 | 3 | Challenging |
| 37 | 6 (`number_6.json`) | 17 | 13 | 24 | 27 | 3 | Challenging |
| 38 | 9 (`number_9.json`) | 17 | 13 | 23 | 28 | 5 | Challenging |
| 39 | HEART (`symbol_HEART.json`) | 16 | 21 | 20 | 28 | 8 | Challenging |
| 40 | 5 (`number_5.json`) | 17 | 14 | 23 | 28 | 5 | Challenging |
| 41 | H (`letter_H.json`) | 17 | 16 | 23 | 28 | 5 | Expert |
| 42 | R (`letter_R.json`) | 18 | 14 | 24 | 30 | 6 | Expert |
| 43 | W (`letter_W.json`) | 18 | 15 | 27 | 27 | 0 | Expert |
| 44 | G (`letter_G.json`) | 18 | 15 | 26 | 28 | 2 | Expert |
| 45 | N (`letter_N.json`) | 18 | 15 | 25 | 29 | 4 | Expert |
| 46 | M (`letter_M.json`) | 18 | 15 | 24 | 30 | 6 | Expert |
| 47 | D (`letter_D.json`) | 18 | 16 | 26 | 28 | 2 | Expert |
| 48 | A (`letter_A.json`) | 18 | 16 | 24 | 30 | 6 | Expert |
| 49 | E (`letter_E.json`) | 18 | 17 | 25 | 29 | 4 | Expert |
| 50 | STAR (`symbol_STAR.json`) | 19 | 18 | 26 | 31 | 5 | Expert |
| 51 | B (`letter_B.json`) | 20 | 17 | 28 | 32 | 4 | Expert |
| 52 | HASH (`symbol_HASH.json`) | 20 | 20 | 29 | 31 | 2 | Expert |
| 53 | AT (`symbol_AT.json`) | 21 | 18 | 30 | 33 | 3 | Expert |

## Next validation stage

Run seeded, full-match simulations with representative policies and dice rolls, record win rates and turn counts by pattern/team, and only then decide whether to revise the difficulty labels or templates.
The current audit does **not** establish strategic reachability or fair win rates.
