# CREATOR — Mathematics, Algorithms, and Design History

**Technical design record · JavaScript prototype → Python engine → Web and Windows v1.0 · October 2026**

> **Scope and evidence.** This document distinguishes **CURRENT** (confirmed rules/code and release checks), **HISTORICAL** (visible in archived JavaScript or Python snapshots), **REVERTED** (explicitly abandoned or reversed), **EXPERIMENTAL** (benchmark-only or evaluated but not adopted), and **PROPOSED** (future mathematical ideas, not implemented). It is a mathematical explanation and development record, **not** a claim that every prototype or discussion can be reconstructed from Git history. The exact post-release AI source should be consulted for line-by-line coefficient verification where archived copies differ.

---

## 1. The mathematical object: a stochastic, adversarial formation game

CREATOR is a two-player, alternating-turn, finite-board strategy game with chance input from a die. Its objective is **spatial completion**, not permanent elimination.

Let

$$

N=16,\qquad \mathcal B={0,\ldots,15}^2,\qquad |\mathcal B|=N^2=256.

$$

Each side starts with 32 pawns, so the initial board has 64 occupied squares and 192 empty squares. The two teams are $T={\mathrm{BLUE},\mathrm{RED}}$.

A useful formal state is

$$

s=(B,P,t,d,\sigma,R,H),

$$

where:

- $B:\mathcal B\to{\varnothing,\mathrm{BLUE},\mathrm{RED}}$ is the board occupancy;

- $P$ is the selected binary victory-pattern matrix;

- $t\in T$ is the player to act;

- $d\in{\bot,1,\ldots,6}$ is the current dice result ($\bot$ means not rolled);

- $\sigma$ is the selected pawn, if any;

- $R$ is the reserve/respawn state;

- $H$ holds statistics and any AI observation state.

Pawn identities, active flags, and home/return handling are represented by the implementation beyond the simplified occupancy function $B$.

**Current rules:** 53 selectable patterns; eight movement directions; one move of any distance from 1 through the die result; jumping over intermediate pawns; friendly destinations prohibited; enemy destinations capturable; captured pawns can return; 100% formation completion; no forced turn cutoff.

This is a **stochastic perfect-information game** in the ordinary gameplay sense: the board and die result are visible, while future dice outcomes are unknown. The implementation's AI algorithms are bounded approximations to game-tree planning, not solutions to the entire game.

---

## 2. Coordinate systems, indexing, and board geometry

### 2.1 Row and column convention

A square is $(r,c)$, where $r$ increases downward and $c$ increases rightward:

$$

0\le r,c<16.

$$

Top home rows are $r\in{0,1}$; bottom home rows are $r\in{14,15}$. At the beginning of a match, each team fills two 16-square home rows:

$$

2\times16=32\text{ pawns per side}.

$$

### 2.2 Embedding a pattern

For a pattern $P$ of side length $k$, let $P\_{ij}\in{0,1}$. The centered placement offset in the engine is

$$

o=\left\lfloor\frac{N-k}{2}\right\rfloor.

$$

The unmirrored target set is

$$

F(P)={(i+o,j+o)\mid P\_{ij}=1}.

$$

For the archived JavaScript prototype's fixed $k=7$,

$$

o=\left\lfloor\frac{16-7}{2}\right\rfloor=4.

$$

Thus its 7×7 mask occupies the coordinate envelope $r,c\in[4,10]$. Because the board has even side length and the mask has odd side length, integer centering leaves one more unused row/column on one side; this is a discrete-grid property, not a rendering error.

The current engine uses the selected pattern's `size`, not an unconditional 7.

### 2.3 The RED vertical mirror — CURRENT

The transformation

$$

M(r,c)=(N-1-r,c)=(15-r,c)

$$

reflects a board square vertically. The two target sets are

$$

F\_{\mathrm{BLUE}}=F(P),\qquad

F\_{\mathrm{RED}}={M(x)\mid x\in F(P)}.

$$

Important algebraic properties:

$$

M(M(r,c))=(r,c),\qquad |F\_{\mathrm{BLUE}}|=|F\_{\mathrm{RED}}|.

$$

The reflection is an **involution**: applying it twice restores the original square. It changes rows, **not columns**. It does **not** send RED to an entirely separate target region; both patterns are in the central board area.

The sets can overlap:

$$

I=F\_{\mathrm{BLUE}}\cap F\_{\mathrm{RED}},\qquad

U=F\_{\mathrm{BLUE}}\cup F\_{\mathrm{RED}}.

$$

By inclusion–exclusion,

$$

|U|=2|F(P)|-|I|.

$$

A vertically symmetric pattern satisfies $F\_{\mathrm{BLUE}}=F\_{\mathrm{RED}}$, so all its targets overlap. An asymmetric pattern can have BLUE-only, RED-only, and shared cells. The implementation history records that **48 of the 53 formations have at least one shared target cell**; this is an overlap count, **not** a claim that 48 patterns have identical target sets.

**Crucial:** overlapping target **coordinates** do not mean two pawns can occupy one square. The board has at most one pawn per square, so occupying a contested cell for BLUE necessarily denies that cell to RED.

### 2.4 Historical target-set models


| Model | Mathematical definition | Status |
|---|---|---|
| One shared mask | $F_B=F_R=F(P)$ | **HISTORICAL / SUPERSEDED** in older JavaScript and an archived Python snapshot |
| Mirrored mask | $F_R=M(F_B)$ | **CURRENT** |
| Separate, non-overlapping goals | $F_B\cap F_R=\varnothing$ by design | **NOT** the current game; do not infer this from the word “mirror” |

Some older tests asserted $F_B=F_R$. Those assertions were updated to test the mirror relation. The fix preserved the intended overlap and did not change the win threshold.

---

## 3. Dice: probability, fairness, and control

### 3.1 The die

The engine draws an integer $D$ from ${1,2,3,4,5,6}$, intended to be uniform:

$$

\Pr(D=d)=\frac16.

$$

The expected roll is

$$

\mathbb E[D]=\frac{1+2+3+4+5+6}{6}=3.5.

$$

Its variance is

$$

\operatorname{Var}(D)=\frac{35}{12}\approx2.9167.

$$

This describes the **random input**, not the number of legal destinations or the distance a player actually chooses.

### 3.2 Exact-distance movement — HISTORICAL / REVERTED

The archived `game screen/game.js` prototype generated one endpoint per direction:

```javascript

nr = r + dr * diceRoll;

nc = c + dc * diceRoll;

```

Mathematically, the candidate endpoints were

$$

(r',c')=(r,c)+D(\Delta r,\Delta c).

$$

That was an **exact-distance** rule: roll 6, travel exactly 6 squares. It gave at most eight geometric candidates before occupancy and edge filtering.

### 3.3 Maximum-distance movement — CURRENT

The current rule treats the roll as an upper bound:

$$

1\le \ell\le D,\qquad

(r',c')=(r,c)+\ell(\Delta r,\Delta c).

$$

This produces up to $8D$ geometric candidates per pawn before filtering. For a roll of 6, that is up to 48 candidate endpoints (many fewer near edges or friendly pieces).

If one temporarily ignores board boundaries and occupancy, the expected candidate count per pawn is

$$

\mathbb E[8D]=8(3.5)=28.

$$

That is **not** an observed average branching factor: the actual legal-move count depends on the square, pawns, and current die.

### 3.4 Dice are independent of AI — CURRENT

AI receives the die outcome; it does not choose the roll. A legal AI action must satisfy the same $1\le\ell\le D$ rule as a human move. This separates:

1. **Chance** — what the die produced;

2. **Decision** — which pawn and endpoint the player chooses.

In the advanced search, future rolls are enumerated as six equally weighted chance branches. This models uncertainty without giving the AI control over it.

---

## 4. Movement geometry and legal actions

The direction set is

$$

\mathcal D={(-1,0),(1,0),(0,-1),(0,1),

(-1,-1),(-1,1),(1,-1),(1,1)}.

$$

For an active pawn $p$ at $x=(r,c)$, roll $d$, and a direction $v\in\mathcal D$, define $y=x+\ell v$. The move is legal if

$$

1\le\ell\le d,\quad y\in\mathcal B,\quad B(y)\ne\operatorname{team}(p).

$$

The last condition allows either an empty destination or an enemy pawn.

**No path-clearance condition appears in the current move generator.** Intermediate squares may contain either team's pawns. In chess terminology, the pawn “jumps” over them.

The set of legal moves for a pawn is

$$

A(p,s,d)={y\mid \exists v\in\mathcal D,\\;1\le\ell\le d,\\;

y=x+\ell v,\\;y\in\mathcal B,\\;B(y)\ne\operatorname{team}(p)}.

$$

The complete action set is

$$

A_t(s,d)={(p,y)\mid p\text{ is active and belongs to }t,\\;y\in A(p,s,d)}.

$$

The engine's generator iterates distances and directions. With $m$ active pawns, candidate generation is bounded by $O(8dm)$, ignoring constant-time board lookups. This is a move-generation bound, not a full AI-search bound.

### 4.1 Distances used in AI

The Basic, Learning, and Advanced heuristics use **Manhattan distance**:

$$

d_1((r,c),(u,v))=|r-u|+|c-v|.

$$

Manhattan distance is a cheap measure of closeness to a target. It is **not** the exact minimum number of CREATOR moves: diagonal movement, jumping, and the die can make true travel cost very different.

A plausible geometric alternative is Chebyshev distance,

$$

d\_\infty((r,c),(u,v))=\max(|r-u|,|c-v|),

$$

because the eight directions permit diagonal movement. But $d\_\infty$ is **not documented as the current AI's proximity metric**; it is discussed later as a proposed experiment.

---

## 5. Capture, respawn, and conservation of occupancy

For a legal move $x\to y$:

1. The moving pawn vacates $x$.

2. It occupies $y$.

3. If $y$ contained an enemy pawn, that enemy is captured.

4. The capture/return system handles its later re-entry, including reserve handling if home squares are blocked.

A capture therefore changes both local occupancy and future pawn availability. The game does **not** implement a permanent “reduce the opponent to zero pieces” victory condition.

Let $C_t$ be the cumulative captures suffered by team $t$. It is a match statistic, not a life limit:

$$

C_t\in\mathbb Z\_{\ge0}

$$

with no fixed maximum prescribed by the rules. “Unlimited respawns” means there is no finite total-return allowance; it does **not** mean every captured pawn must instantly reappear on an occupied home square.

The archived JavaScript prototype used a simple `returnPawnHome` scan of the two home rows and returned `false` when none was empty. Later Python handling added reserve logic. The exact timing of reserve deployment is an engine implementation detail and should be verified against `engine/capture.py` and `engine/game.py` before documenting it as a formula.

---

## 6. Formation completion: the winning equation

For team $t$, let

$$

F_t=\text{its target set},\qquad K_t=|F_t|.

$$

Its occupied-target count is

$$

h_t(s)=\sum\_{x\in F_t}\mathbf1[B(x)=t].

$$

The completion ratio is

$$

q_t(s)=\frac{h_t(s)}{K_t}\quad(K_t>0).

$$

The **CURRENT** victory condition is

$$

\boxed{\operatorname{Win}(t,s)\iff K_t>0\\;\land\\;h_t(s)=K_t.}

$$

Equivalently, $q_t=1$: **100% simultaneous occupation** of that team's own target set. Merely having occupied a target earlier does not count.

### 6.1 The 75% threshold — HISTORICAL / REVERTED

An archived Python `engine/victory.py` contained

```python

VICTORY_FRACTION = .75

required_count = ceil(K * VICTORY_FRACTION)

```

and recognized a win when

$$

h_t\ge\lceil0.75K_t\rceil.

$$

This was replaced by the full-formation condition. Example: for a 20-cell target, the historical threshold was 15; the current threshold is 20.

### 6.2 Turn-400 evaluation — HISTORICAL / REMOVED FROM GAMEPLAY

An archived implementation declared `TURN_LIMIT = 400` and included a comparison of relative progress. The comparison can be expressed without floating-point division as

$$

h_BK_R\\;\mathop{\gtrless}\\;h_RK_B,

$$

equivalent to comparing $h_B/K_B$ with $h_R/K_R$ when both target sizes are nonzero.

The current `TURN_LIMIT` is `None`, and `endgame_result` returns no occupancy-based winner. **No automatic win or draw occurs at turn 400.** A benchmark may stop at 400 moves for practical measurement; such a stop is **censoring**, not a completed match.

### 6.3 A structural feasibility constraint

Since a side has 32 pawns initially, a target with $K_t>32$ cannot be simultaneously occupied by that side unless the rules allow it to control more than 32 pawns (the current rules do not claim that). A sensible pattern-validation invariant is therefore

$$

0\<K_t\le32.

$$

This is a **mathematical design check**, not a claim that every archived pattern file has been independently audited here.

---

## 7. The JavaScript stage: original algorithms and limitations

The archived browser prototype used a 16×16 array:

```javascript

Array.from({ length: 16 }, *()* => Array(16).fill(null))

```

It represented players as `"C"` (Creator) and `"D"` (Destroyer), not the later symmetric BLUE/RED labels. It used a 7×7 pattern placed with offset 4, a simple home-row reset, and an `X` fallback mask if pattern loading failed.

### 7.1 Fallback X pattern

For $k=7$, the two diagonals are

$$

{(i,i):0\le i<7}\cup{(i,6-i):0\le i<7}.

$$

Their union contains $7+7-1=13$ cells because the center belongs to both diagonals.

### 7.2 Prototype win detection

The JavaScript `checkWin(player)` scanned the full 16×16 board and returned false if **any active pattern cell** was not occupied by that player. Thus that particular archived prototype already used complete-pattern checking, even though a later archived Python snapshot experimented with a 75% threshold. **The development history is not a simple monotonic sequence of stricter rules.**

### 7.3 Prototype return logic

The JavaScript `returnPawnHome(player)` scanned the team's two home rows in row-major order and filled the first empty square. It was deterministic given the board, but lacked the later documented reserve handling.

### 7.4 Rendering mathematics

For canvas width $W$, the prototype used

$$

\text{cellSize}=W/16,

$$

and drew cell $(r,c)$ at pixel origin

$$

(x,y)=(c\cdot\text{cellSize},r\cdot\text{cellSize}).

$$

The later desktop renderer used a logical cell size of 48 pixels and a board origin, while native display scaling mapped logical coordinates through

$$

x\_{\mathrm{screen}}=\operatorname{round}(o_x+s\\,x\_{\mathrm{logical}}),\quad

y\_{\mathrm{screen}}=\operatorname{round}(o_y+s\\,y\_{\mathrm{logical}}).

$$

These are presentation transformations, not game-rule transformations.

---

## 8. Basic AI: greedy move scoring

Basic AI enumerates legal moves, assigns a score, and chooses the highest-scoring action:

$$

a^*=\arg\max\_{a\in A_t(s,d)}S\_{\mathrm{basic}}(a).

$$

An archived later implementation (from the supplied mobile-source snapshot) contains the following additive terms. Define:

- $L=1$ if the destination is in the AI's target set;

- $C=1$ if the destination captures an enemy;

- $Q=1$ if the origin is in the target set;

- $H=1$ if the move develops a pawn out of its home rows;

- $d\_{\mathrm{old}},d\_{\mathrm{new}}$ as minimum Manhattan distances to an unfilled AI target;

- $\Delta=d\_{\mathrm{old}}-d\_{\mathrm{new}}$.

Its visible heuristic can be summarized as

$$

\begin{aligned}

S\_{\mathrm{basic}}(a)={}&100L+50C+60C L\\\\

&-90Q(1-L)(1-C)+15H\\\\

&+6\Delta-1.2d\_{\mathrm{new}}\\\\

&+5\mathbf1[d\_{\mathrm{old}}>6]

+20C\mathbf1[\Delta>0]\\\\

&-10\mathbf1[\neg C\land\neg L\land\Delta\le0]

+\varepsilon,

\end{aligned}

$$

where $\varepsilon\sim U(0,0.8)$ is a small random tie-breaker. Distance-dependent terms are evaluated only when the archived code finds unfilled targets; the indicator terms reflect the source's conditional branches.

The terms express priorities:

- occupy a required square;

- capture, especially on a required square;

- avoid abandoning a useful occupied square;

- develop pawns from home;

- move closer to incomplete targets;

- penalize aimless moves.

**Version caveat:** these coefficients are verified from a supplied archived source snapshot. Basic AI was later revised and committed as part of the mirrored-target fixes. Treat this equation as a **documented implementation stage**, not a guarantee that every numeric coefficient matches the newest GitHub `main` without inspecting it.

### 8.1 Why greedy scoring is not optimal play

The maximum-scoring immediate move need not maximize eventual win probability. For example, moving onto a target may create an immediate gain of +100 but expose several critical squares to capture. Basic AI does not solve that long-horizon adversarial tradeoff.

---

## 9. Learning AI: adaptive heuristic, not necessarily neural learning

The archived Learning AI records opponent behavior:

$$

n=\text{observed opponent moves},\quad

c=\text{observed opponent captures},\quad

p=\text{observed opponent target-landings}.

$$

For $n>0$, it computes

$$

a=c/n,\qquad f=p/n.

$$

The visible archived decision table was:

| Condition | Pattern weight | Capture weight | Proximity penalty |

|---|---:|---:|---:|

| Fewer than 2 observations | 100 | 40 | 2.0 |

| Opponent aggression $a>0.35$ | 140 | 25 | 3.5 |

| Otherwise opponent formation focus $f>0.40$ | 80 | 75 | 2.0 |

| Otherwise | 100 | 45 | 2.5 |

The aggression condition takes precedence over the pattern-focus condition.

For candidate action $a$, the archived score was

$$

S\_{\mathrm{learn}}(a)

=w_P\mathbf1[\text{destination in own targets}]

+w_C\mathbf1[\text{capture}]

-w_D\min\_{z\in U_t}d_1(\text{destination},z)

+\varepsilon,

$$

where $U_t$ is the set of own targets not currently held by the AI, and $\varepsilon\sim U(0,1)$.

This is **online rule-based adaptation** using observed frequencies. It should **not** be described as a trained neural network, gradient descent, Q-learning, or reinforcement learning unless those algorithms are separately implemented. Its weights change in response to observed play, not by fitting a differentiable model.

As with Basic AI, archived weights document a stage of development; later code may contain improvements.

---

## 10. Advanced AI: chance nodes, opponent replies, and static evaluation

Advanced AI considers the immediate consequences of its move and the opponent's possible replies under future die outcomes.

Let $T(s,a)$ denote a simulated state after action $a$, and $V(s)$ a heuristic evaluation from the AI's perspective.

### 10.1 Expectation over future dice

For a candidate AI move $a$, the one-opponent-response estimate is

$$

Q(s,a)=\frac16\sum\_{d=1}^{6}

\min\_{b\in A\_{\mathrm{opp}}(T(s,a),d)}

V(T(T(s,a),b)).

$$

If a particular die yields no legal opponent reply, the evaluator uses the state without that reply for that branch. The AI chooses approximately

$$

a^*=\arg\max\_{a\in A\_{\mathrm{AI}}(s,D)}Q(s,a).

$$

This is an **expectiminimax-style, depth-limited** search:

1. AI chooses a move (**max**);

2. next die is a chance event (**average**);

3. opponent chooses its best counter (**min**);

4. evaluate the resulting position (**heuristic leaf**).

The archived code checks for an immediate AI win before evaluating all opponent responses.

### 10.2 Static evaluation

A documented Advanced AI stage used

$$

V(s)=

200(h\_{\mathrm{AI}}-h\_{\mathrm{opp}})

+15C\_{\mathrm{opp}}-20C\_{\mathrm{AI}}

-1.5\sum\_{p\in P\_{\mathrm{AI}}^{\mathrm{active}}\setminus F\_{\mathrm{AI}}}

\min\_{z\in U\_{\mathrm{AI}}}d_1(p,z),

$$

with terminal overrides

$$

V(s)=

\begin{cases}

+10{,}000,&\text{AI completed its formation},\\\\

-10{,}000,&\text{opponent completed its formation},\\\\

\text{heuristic above},&\text{otherwise}.

\end{cases}

$$

Here $h\_{\mathrm{AI}}$ and $h\_{\mathrm{opp}}$ must be measured on **each team's own target set**. Using the AI's target set to measure both sides would be mathematically wrong when the targets are mirrored.

The capture counters are **captures suffered** in the archived formula. Their use is a heuristic measure of disruption/attrition, not a permanent-material victory rule.

### 10.3 Simulation and undo

Instead of cloning the entire game for every leaf, the search temporarily:

1. saves the pawn's origin and any destination occupant;

2. moves the pawn in the board array;

3. temporarily deactivates a captured pawn;

4. evaluates the resulting board;

5. restores the original state.

Correct undo is an invariant:

$$

\operatorname{Undo}(\operatorname{Apply}(s,a))=s.

$$

This must include board cells, pawn coordinates, active status, and any mutable dice state touched by the simulation. A failure to restore state can make later candidate evaluations depend on the order of search.

### 10.4 Branching cost

Let $A$ be the number of legal AI moves and $B_d$ the number of legal opponent replies for die $d$. A simplified leaf count is

$$

L\approx\sum\_{a=1}^{A}\sum\_{d=1}^{6}\max(1,B_d).

$$

If $B_d\approx B$, this is $O(6AB)$ leaf evaluations. Each leaf also incurs the cost of checking formation occupancy and heuristic distances. This explains why Advanced AI is much slower than a single-pass greedy agent.

The search is **not** an exhaustive proof of victory, nor is it full-depth minimax.

---

## 11. Optimization history: successful, reverted, and unproven

### 11.1 Mirrored-opponent evaluation — CURRENT

Advanced AI must count opponent progress on $F\_{\mathrm{opp}}$, not $F\_{\mathrm{AI}}$. This was corrected along with mirrored formation testing. It matters whenever $F\_{\mathrm{BLUE}}\ne F\_{\mathrm{RED}}$.

### 11.2 Duplicate response evaluation caching — ADOPTED

The development record reports an Advanced AI experiment over 10 moves:

| Evaluation approach | Time |

|---|---:|

| Without the response-evaluation cache | 150.04 s |

| With the cache | 35.91 s |

Relative reduction:

$$

\frac{150.04-35.91}{150.04}\times100%\approx76.1%.

$$

This is a measured result for that experiment, **not** a universal runtime guarantee. A cache is valid only when its key captures every part of the state affecting the value. Reusing an evaluation across distinct board positions would be incorrect.

### 11.3 Static target and terminal-check reuse — ADOPTED

In the final optimization, the Advanced AI evaluation avoids recomputing the same target coordinates and repeated victory checks at each leaf. The opponent target set is cached by a key containing board size, pattern size, and pattern-grid contents. The evaluator counts target occupancy once and applies the same terminal priority as before.

A recorded comparison on **seed 57, die 4, EXCLAMATION pattern, BLUE AI**:

| Version | Time | Selected move |

|---|---:|---|

| Before | 7.51 s | `(1, 3, 5, 7)` |

| After | 5.95 s | `(1, 3, 5, 7)` |

Speedup:

$$

\frac{7.51}{5.95}\approx1.26\times,

$$

or a time reduction of approximately

$$

\frac{7.51-5.95}{7.51}\times100%\approx20.8%.

$$

The identical move is evidence of unchanged choice **for this test case**, not a formal proof of identical decisions for every possible state.

### 11.4 Pawn-position distance cache — EXPERIMENTAL / REVERTED

An attempted distance cache keyed by pawn position increased the observed time of one move to **8.21 s**. It was reverted. This illustrates an important optimization principle:

$$

\text{cache benefit}=

\text{recomputation avoided}

-\text{lookup, key construction, and memory overhead}.

$$

Caching is not automatically faster. A key based only on pawn position can also be logically insufficient if the set of unfilled targets changes between simulated states.

### 11.5 General caution

A performance optimization must preserve the **value function**, terminal ordering, simulation state, and legal action set. Comparing only runtime without checking move choice or regression tests is insufficient.

---

## 12. Benchmark mathematics and interpretation

### 12.1 Paired experiments

AI comparisons used controlled seeds and paired conditions where possible. If two strategies are evaluated under comparable dice seeds and patterns, pairing reduces noise from random chance.

For a measured quantity $X$, a paired difference is

$$

\Delta_i=X\_{i,\mathrm{new}}-X\_{i,\mathrm{old}}.

$$

Its sample mean is

$$

\bar\Delta=\frac1n\sum\_{i=1}^{n}\Delta_i.

$$

This is more informative than comparing unrelated samples when the same scenarios can be reused.

### 12.2 Observed Basic/Learning benchmark

A documented benchmark comprised **424 games** with a **benchmark-only 400-move stopping condition**:

- 41 completed formation victories;

- 383 unfinished at the experimental cutoff;

- 20 BLUE victories and 21 RED victories among completed games.

The observed completed-game fraction is

$$

\frac{41}{424}\approx9.67%.

$$

The unfinished fraction is

$$

\frac{383}{424}\approx90.33%.

$$

These are **sample outcomes under the benchmark protocol**, not probabilities of ever winning an unrestricted match.

Among the 41 completed matches, the observed BLUE share was

$$

20/41\approx48.78%,

$$

and RED share was $21/41\approx51.22%$. With so few completed games and heavy censoring, these values are not evidence of exact competitive balance.

### 12.3 Censoring versus draws

Let $T$ be the move number at which a game completes its formation. A benchmark cutoff $C=400$ records

$$

Y=\min(T,C),\qquad \delta=\mathbf1[T\le C].

$$

If $\delta=0$, the observation is **right-censored**: the experiment ended before victory. It is **not** a draw under the current rules.

### 12.4 What benchmarks can and cannot establish

Benchmarks can measure move legality, runtime, completion rates under a specified cutoff, and empirical side differences. They do **not** by themselves establish:

- that every pattern is easy or guaranteed to complete;

- that a particular AI is optimal;

- that RED and BLUE are exactly equal in strength;

- that a 400-move stop is a gameplay rule;

- that a single faster move implies a universal speedup.

Repository benchmark artifacts include `analysis/benchmark_before_ai_fixes.csv`, `analysis/benchmark_basic_after_fix.csv`, `analysis/benchmark_learning_after_fix.csv`, `analysis/benchmark_after_mirror.csv`, and `benchmark_52k_results.csv`. Their names identify recorded experiments; precise statistical conclusions should be derived from the files and their experimental settings.

---

## 13. The Windows-versus-web mirror issue: a set-theory/display distinction

A release-stage mismatch arose because the Windows renderers drew

$$

F\_{\mathrm{BLUE}}\cup F\_{\mathrm{RED}},

$$

using BLUE outlines for BLUE-only squares, RED outlines for RED-only squares, and purple for overlaps. The browser instead exposed the **current player's** target set.

The first attempted desktop change made all union outlines purple:

$$

\text{draw}(F_B\cup F_R,\text{purple}).

$$

That changed only the colors and **did not fix the shape**.

The successful change was

$$

\boxed{\text{draw}(F_t,\text{purple}),\quad t=\text{current player}.}

$$

When the turn switches, the visible formation switches between $F_B$ and $F_R$. This matches the browser presentation while leaving victory rules and AI target sets unchanged.

**Lesson:** visual union, visual intersection, and per-player target sets are mathematically distinct objects. A rendering bug should not be “fixed” by weakening the underlying game rules.

---

## 14. Testing as mathematical invariants

The final development checks reported **730 passing tests** after updating obsolete shared-target assertions. The Windows executable and extracted ZIP were also manually launch-tested.

Core invariants worth preserving include:

### 14.1 Movement

For every generated action:

$$

0\le r',c'<16,\qquad 1\le\ell\le d,\qquad

(\Delta r,\Delta c)\in\mathcal D,\qquad B(r',c')\ne t.

$$

Intermediate occupancy must not invalidate an otherwise legal jump.

### 14.2 Target reflection

For each pattern,

$$

F_R={(15-r,c):(r,c)\in F_B}.

$$

This is stronger and more accurate than the discarded assertion $F_R=F_B$.

### 14.3 Victory

$$

\operatorname{Win}(t,s)\iff

|F_t|>0\land\forall x\in F_t,\ B(x)=t.

$$

No 75% threshold; no forced turn-400 winner.

### 14.4 AI fairness

Every AI-selected move must belong to $A_t(s,d)$. The AI may choose an action but not override the die.

### 14.5 State restoration

After any simulated move and undo, all relevant state should equal its pre-simulation state. Property-based tests are especially useful here because a bug may appear only after captures or unusual board configurations.

---

## 15. Computational complexity and limits

| Operation | Approximate bound | Important qualifier |

|---|---|---|

| Scan board | $O(N^2)$ | $N=16$ fixed in current game |

| Construct target set | $O(k^2)$ | Pattern size $k$ |

| Count occupied targets | $O(K)$ | $K=|F_t|$ |

| Generate one pawn's moves | $O(8d)$ | Constant-time occupancy lookup |

| Generate all moves | $O(8dm)$ | $m$ active pawns |

| Greedy AI selection | $O(A\cdot E)$ | $E$ = move-scoring cost |

| One-response expectiminimax | $O(6AB\cdot E)$ | Approximate branching $A,B$ |

The **state space** is enormous. Even if one ignores pawn identity, reserve state, dice, and turn, a board with three possible values per square has up to

$$

3^{256}

$$

occupancy assignments (many are illegal or unreachable). This upper bound explains why exhaustive whole-game search is not practical merely because the board is finite.

With no fixed turn limit and possible repetition, **finite state does not imply that every play sequence must terminate**. Repetition and cycles are possible in principle; the current rules do not claim a forced draw or universal completion guarantee.

---

## 16. Ideas considered, not adopted, or left for future study

This section deliberately separates **recorded historical changes** from **mathematical proposals**. An idea listed as proposed is **not** evidence that it was coded, benchmarked, or scheduled for release.

| Idea | Mathematical formulation | Status / reason |

|---|---|---|

| Exact-distance die | $\ell=D$ | **REVERTED** in favor of $1\le\ell\le D$ |

| 75% completion | $h_t\ge\lceil0.75K_t\rceil$ | **REVERTED**; current rule is 100% |

| Turn-400 adjudication | compare $h_B/K_B$ and $h_R/K_R$ | **REMOVED** from gameplay; experimental cutoffs remain possible |

| Identical target sets | $F_B=F_R$ | **SUPERSEDED** by vertical reflection |

| Separate Creator/Destroyer objectives | asymmetric roles | **HISTORICAL concept**, replaced by symmetric BLUE/RED objectives |

| Pawn-position distance cache | memoize distance by coordinate | **TRIED AND REVERTED** after slower timing |

| More persistent web sessions | database-backed match state | **PLANNED/OPTIONAL**, not a present game rule |

| Online human-versus-human | synchronized network game state | **NOT CURRENTLY PLANNED** in the documented release roadmap |

| Better AI evaluation | improved $V(s)$ and benchmarks | **POSSIBLE FUTURE WORK**, not a promised implementation |

### 16.1 Possible: distance estimates matched to the rules

A more movement-aware heuristic could compare Manhattan and Chebyshev distances, or estimate turns under the die distribution:

$$

\hat\tau(x,z)\approx \frac{d\_\infty(x,z)}{\mathbb E[D]}

=\frac{d\_\infty(x,z)}{3.5}.

$$

**Caution:** this is a rough, unvalidated approximation. It ignores landing restrictions, dice variability, captures, target competition, and turn sequencing. It is **not** a current engine formula.

### 16.2 Possible: assignment-based formation planning

Rather than sum each pawn's distance to its nearest missing target (which can direct many pawns to the same square), assign distinct pawns to distinct targets:

$$

\min\_{\pi}\sum\_{i=1}^{K}c(p\_{\pi(i)},z_i),

$$

where $\pi$ is a one-to-one assignment and $c$ is a travel-cost estimate. This resembles a minimum-cost bipartite matching problem. It could reduce crowding but would add computational cost and still ignore the opponent.

**Status: PROPOSED ONLY.**

### 16.3 Possible: threat-aware target valuation

Let $e(z)$ estimate how easily the opponent can capture or contest target $z$. A richer heuristic could be

$$

V'(s)=V(s)-\lambda\sum\_{z\in F\_{\mathrm{AI}}\cap\mathrm{held}}e(z).

$$

This would value **defensible** formation progress rather than raw occupation alone.

**Status: PROPOSED ONLY.**

### 16.4 Possible: transposition tables

A full search-state cache might use a key such as

$$

K(s)=(B,t,d,P,R,\text{relevant counters}),

$$

rather than pawn position alone. A Zobrist hash could make board-state keys cheaper, but correctness requires capturing all variables that affect move legality or evaluation.

**Status: PROPOSED ONLY.** The reverted position-distance cache is not evidence that a correct full-state transposition table has been implemented.

### 16.5 Possible: rigorous statistical reporting

Future AI studies could report confidence intervals for completed-game proportions and treat benchmark cutoffs as censored observations. Such reporting must specify seed selection, pattern mix, AI versions, side assignments, move caps, and hardware.

**Status: PROPOSED REPORTING IMPROVEMENT.**

---

## 17. Mathematical chronology

| Stage | Main mathematics | Result |

|---|---|---|

| Early JavaScript | 16×16 array, 7×7 centered mask, exact-distance die, eight vectors, complete-mask scan | Playable conceptual prototype with Creator/Destroyer labels |

| Python transition | modular game state, move generation, capture/return handling, AI | Rules centralized outside the renderer |

| Historical Python experiments | 75% completion, turn-400 evaluation | Later discarded as gameplay conditions |

| Rule stabilization | flexible die distance, 100% victory, no forced cutoff | Current gameplay semantics |

| Team symmetry work | BLUE/RED objectives, RED vertical reflection, intentional overlap | Current target mathematics |

| Basic AI | weighted one-ply move scores and Manhattan proximity | Fast heuristic opponent |

| Learning AI | observed capture/formation ratios and dynamic weights | Adaptive heuristic opponent |

| Advanced AI | max/chance/min search, terminal scores, static heuristic, simulate/undo | More expensive opponent-response analysis |

| Optimization | duplicate-evaluation caching, reused target sets and counts | Measured speed improvements |

| Reverted optimization | pawn-position distance cache | Removed after regression |

| Web release | Python server as authority, current-player target rendering | Shared engine with browser interface |

| Windows v1.0 | current-player target rendering in both desktop paths | Matched web mirror presentation; verified extracted ZIP |

This table is a **conceptual history**, not an assertion of exact commit order for every intermediate prototype.

---

## 18. Code and artifact map

These are the relevant repository locations and supplied historical materials:

| Location | Mathematical role |

|---|---|

| `engine/movement.py` | Direction vectors, legal endpoints, dice-distance bounds |

| `engine/dice.py` | Die generation |

| `engine/victory.py` | Target reflection, occupancy counts, 100% win test |

| `engine/game.py` | State transitions and turn sequencing |

| `engine/capture.py` | Capture/return and reserve behavior |

| `engine/ai/basic_ai.py` | Greedy weighted move evaluation |

| `engine/ai/learning_ai.py` | Observation ratios and adaptive weights |

| `engine/ai/advanced_ai.py` | Chance-node response search and board evaluation |

| `ui/renderer.py` | Logical desktop board rendering |

| `ui/native_board.py` | Scaled Windows/native board rendering |

| `web_server.py` | Game state exposed to browser |

| `web/` | Browser display and interactions |

| `patterns/` | Binary target masks |

| `tests/` | Rules and AI regression checks |

| `analysis/*.csv`, `benchmark_52k_results.csv` | Empirical benchmark artifacts |

| Archived `game screen/game.js`, `old/game.js` | JavaScript prototype rules |

| Archived Python source ZIPs | Historical heuristic and victory implementations |

The archived `old/game.js` visibly begins with `//REVERT`. That label supports describing it as a reverted/archive copy; it does **not**, on its own, prove the reason or date of every revert.

---

## 19. Final specification in compact mathematical form

For any selected binary pattern $P$:

$$

\begin{aligned}

\mathcal B&={0,\ldots,15}^2,\\\\

F_B&={(i+o,j+o):P\_{ij}=1},\\\\

F_R&={(15-r,c):(r,c)\in F_B},\\\\

D&\sim\operatorname{Uniform}{1,\ldots,6},\\\\

A_t(s,D)&={(p,p+\ell v):v\in\mathcal D,\ 1\le\ell\le D,\\\\

&\qquad p+\ell v\in\mathcal B,\ B(p+\ell v)\ne t},\\\\

h_t(s)&=\sum\_{x\in F_t}\mathbf1[B(x)=t],\\\\

\operatorname{Win}(t,s)&\iff |F_t|>0\land h_t(s)=|F_t|.

\end{aligned}

$$

There is **no gameplay turn limit**, no percentage-based substitute for victory, and no permanent-elimination win condition.

The essential mathematical idea is simple but demanding: **chance constrains movement, the opponent contests space, and victory requires simultaneous completion of a team-specific geometric set.**

---

## 20. Verification notes and document maintenance

This record was assembled from the supplied README and rule descriptions, the visible archived JavaScript and Python source packages, the displayed current `engine/victory.py` and renderer code, and the recorded test/benchmark/release outcomes in the development conversation.

**Confirmed at the final Windows v1.0 check:** the desktop game rebuilt successfully, the current-player mirrored formation displayed correctly, gameplay was manually tested, and the extracted Windows ZIP launched. The repository's recent AI and rendering fixes were pushed to `main`.

**Not independently verified in this document:** every historical intermediate branch, all 53 pattern JSON files, exact coefficients of the very latest post-optimization Basic/Learning implementations, the full mobile app release state, and statistical reanalysis of every CSV. No undocumented AI algorithm or abandoned feature is presented as fact.

For future revisions, keep three records distinct:

1. **Rules:** mathematical invariants that define a valid CREATOR match.

2. **Algorithms:** current implementations and their version-specific coefficients.

3. **Experiments:** benchmark conditions, performance measurements, discarded approaches, and proposals.

That separation prevents a historical experiment from accidentally becoming a claimed current game rule.

---

**CREATOR — Mathematics and Algorithms · Technical companion to `README.md` and the official rulebook.**
