<div align="center">

# CREATOR

**A tactical board game you can never complete**

[![Play Online](https://img.shields.io/badge/Play-Online-brightgreen)](https://creator-game.onrender.com/)
[![Python](https://img.shields.io/badge/Python-Game_Engine-blue)](https://www.python.org/)
![Board](https://img.shields.io/badge/Board-16%C3%9716-394b63)
![Patterns](https://img.shields.io/badge/Formations-53-purple)
![AI](https://img.shields.io/badge/AI-3_Opponents-orange)

**[Play Creator](https://creator-game.onrender.com/) · [Repository](https://github.com/dkconnect/Creator) · [Developer](https://github.com/dkconnect)**

**Dibyanshu Kumar | October 2026**

</div>

---

# What is Creator?

Creator is a two-player strategy game played on a **16 × 16 board**, with **32 pawns on each side**. Instead of winning by eliminating the opponent, a player wins by occupying every cell of a selected geometric formation with their own pawns.

The board is shared. The formation is shared. Both players are trying to construct the same pattern while interrupting each other's progress.

A six-sided die controls how far a pawn *may* move, but not exactly how far it *must* move. A roll of six allows a move of one, two, three, four, five, or six squares. Pawns can move in eight directions, jump over other pieces, and capture enemies on their destination squares. Captured pieces can return, so a tactical advantage is rarely permanent.

> **Creator is about occupying the right squares, not simply removing the other player's pieces.**

The project includes a Python game engine, a Pygame desktop interface, three AI opponents, tests and benchmarks, and a browser version backed by the same Python engine.

**Play now:** https://creator-game.onrender.com/

---

# The idea

The starting question was simple: *what if a board game were won by creating a shape rather than capturing a king or clearing the board?*

That changes how individual moves matter. A square can be valuable because it belongs to the final formation, because it blocks an opponent's route, or because occupying it at the right moment completes the whole pattern. A capture can interrupt a formation, but it does not end a pawn's participation forever.

The dice introduce uncertainty without taking all choice away from the player. The player still chooses **which pawn to move, which direction to take, and how many squares to travel** within the roll's limit.

Creator therefore sits between a formation puzzle and an adversarial board game: planning matters, but the opponent and the dice continuously change what is possible.

---

# Play Creator

The browser version is available at **[creator-game.onrender.com](https://creator-game.onrender.com/)**.

On the opening screen, select a game mode and one of the 53 victory formations. Then start the match. The game board opens in a separate, screen-fitted view with the dice, current turn, capture statistics, and match controls beside it.

Available modes:

| Mode | BLUE | RED |
| --- | --- | --- |
| Human vs Human | Human | Human |
| Human vs Basic AI | Human | Basic AI |
| Human vs Learning AI | Human | Learning AI |
| Human vs Advanced AI | Human | Advanced AI |

BLUE moves first. In AI modes, the human plays BLUE and the Python AI plays RED.

The website runs on a free hosting tier. It may take a little longer to open after a period of inactivity, and a match can reset when the server restarts. Matches are not currently saved permanently.

---

# How the game works

## The board and the objective

Creator uses a 16 × 16 grid: **256 squares**, shared by BLUE and RED. Each team starts with 32 pawns. Before a match, the players select one victory pattern from the available pattern library.

Both teams compete for the **same centered formation**. To win, a team must occupy **100% of the required cells at the same time**. Occupying most of the shape does not count as a victory.

## Dice and movement

At the start of a turn, the active player rolls a standard six-sided die. The result is the **maximum** distance for one move, not a compulsory exact distance.

| Roll | Legal movement distance |
| --- | --- |
| 1 | 1 square |
| 2 | 1 or 2 squares |
| 3 | 1, 2, or 3 squares |
| 4 | 1–4 squares |
| 5 | 1–5 squares |
| 6 | 1–6 squares |

A pawn moves in one straight line, in any of eight directions: north, northeast, east, southeast, south, southwest, west, or northwest. A move must stay inside the board.

Pawns may **jump over intermediate pieces**. What matters for occupancy is the destination: a pawn cannot land on a friendly pawn, but it may land on an opposing pawn and capture it.

## Captures and returns

Captured pawns are not permanently eliminated. The engine supports unlimited respawns, with reserve handling when home squares are occupied. This makes capture a positional and tactical action rather than permanent material destruction.

The displayed capture totals are match statistics, not a limit on how many times a piece can return.

## Winning and game length

A player wins by completing the selected formation with their own pawns. There is **no fixed turn limit** and no automatic victory or draw at turn 400. A game continues until the engine recognizes a completed formation.

For the complete player-facing rules and examples, see the official rulebook when published in the repository and linked from the website.

---

# From a browser idea to a Python game

Creator did not begin as a finished Python application. Its development moved through different approaches as the rules, AI, and interface became more demanding.

## The original JavaScript direction

The earliest direction was browser-oriented. A visual board was a natural place to begin: it made movement, pawn positions, and the intended formation easy to inspect. But as the game grew, keeping the rules consistent across rendering, turn management, captures, respawns, and AI became more important than the original frontend technology.

The project moved toward a **single authoritative Python engine**. That decision shaped the rest of Creator: rules would live in the engine, while interfaces would display the state and submit player actions.

## The Python/Pygame phase

The desktop version provided a direct way to test the game interactively while separating board representation, legal moves, dice, turn progression, patterns, victory checks, and AI decision-making.

This separation mattered because several gameplay details changed during development. A correction to movement or victory should be made once in the engine, not independently in every interface.

Pygame remained the desktop presentation layer; it was not intended to be the authority on whether a move or victory was legal.

## Building AI opponents

Creator developed three Python opponents: **Basic**, **Learning**, and **Advanced**. They use the game's legal state and moves to choose actions at different levels of sophistication.

An important design boundary emerged during AI development: **the AI does not control the die**. Dice are generated independently by the engine, and the agent receives the actual result before choosing a legal move. This avoids giving an AI an unfair advantage through dice manipulation.

The names describe distinct implemented agents; they should not be read as a published scientific ranking of their playing strength. Benchmark results depend on patterns, match conditions, and sample size.

## Returning to the web

Once the Python game and AI were established, the project returned to the browser without reimplementing the rules in JavaScript.

A small Python HTTP server exposes the game state and actions as JSON. The browser renders the board and sends requests; the Python engine validates and executes them.

```text
Browser interface
      |
      | JSON requests / responses
      v
Python web server
      |
      v
Game engine ---- Dice / legal moves / victory
      |
      +---- Basic AI
      +---- Learning AI
      +---- Advanced AI
```

This is a deliberate architectural choice: the desktop and browser editions share the same game rules rather than gradually becoming two different games.

---

# The web interface

The browser edition went through its own iterations.

The first functional interface exposed the board and basic controls. AI support was then connected to the existing Python agents. After that, the focus moved from adding features to making the game usable on ordinary laptop and mobile screens.

A full 16 × 16 board can easily become taller than a browser window. The interface was therefore redesigned into **two distinct screens**:

1. **Home:** choose Human vs Human or an AI opponent, select a formation, and start the match.
2. **Game:** play on a viewport-fitted board with dice, turn information, capture counts, and a way to return to setup.

The final polish added a shared Rulebook link, a creator credit in the footer, clearer controls, and responsive styling. The website intentionally does **not** provide online human-versus-human networking; Human vs Human is local turn-taking within one browser session.

---

# The engine and its boundaries

Creator's Python engine is responsible for the state of a match. In the web edition, the server acts as the bridge between that engine and the interface.

The relevant modules include:

| Component | Responsibility |
| --- | --- |
| `engine/game.py` | Game state and turn progression |
| `engine/dice.py` | Dice generation independent of AI |
| `engine/victory.py` | Formation target and victory evaluation |
| `engine/ai/basic_ai.py` | Basic opponent |
| `engine/ai/learning_ai.py` | Learning opponent |
| `engine/ai/advanced_ai.py` | Advanced opponent |
| `patterns/` | JSON formation definitions |
| `web_server.py` | HTTP API and per-visitor game sessions |
| `web/` | Browser interface |

The web API uses the following routes:

| Route | Purpose |
| --- | --- |
| `GET /api/patterns` | List available formations |
| `GET /api/state` | Read the current visitor's match |
| `POST /api/new` | Start a match with a pattern and mode |
| `POST /api/roll` | Roll the current player's die |
| `POST /api/select` | Select a pawn |
| `POST /api/move` | Attempt a move |
| `POST /api/ai` | Advance an AI turn |
| `GET /health` | Hosting health check, where enabled |

The server validates requested actions. A browser cannot simply declare a winning move or choose the AI's dice result.

---

# Development decisions that changed the game

The development history is worth keeping because several decisions were not cosmetic: they changed what Creator *is*.

## Flexible movement instead of exact-distance movement

An earlier interpretation treated the dice roll as an exact number of squares. The current rule treats it as a **maximum distance**. That gives the player more meaningful choices on each turn and is the rule enforced by the current game.

## Formation completion instead of partial victory

Intermediate experiments and discussions considered easier or percentage-based victory conditions. The current game requires **every target cell**. A formation that is 75% complete is progress, not a win.

## Symmetric BLUE and RED objectives

Older descriptions explored asymmetric Creator/Destroyer roles. The current game instead gives both teams the same selected centered formation and the same fundamental movement rules. This makes the contest a direct race and struggle for board control.

## Respawns instead of permanent elimination

Captures are significant, but they do not permanently reduce the number of pawns a team can use. Unlimited returns and reserve handling keep the formation objective central throughout a match.

## No artificial turn-400 result

A fixed-turn cutoff may be useful when running experiments, but it should not decide an actual game. The playable game has no turn-400 forced winner or draw. Benchmark stopping conditions are separate from gameplay victory.

## Independent dice for fair AI comparisons

The dice belong to the engine, not to an AI strategy. AI agents are evaluated on the moves they select from the rolls they receive, not on their ability to choose favorable rolls.

## One engine, multiple interfaces

Rather than rebuilding all rules in JavaScript for hosting, Creator retained Python as the source of truth. The browser is a client of that engine, which reduces the risk of different rules on desktop and web.

These are the important **design reversals and corrections**. They are described here as development decisions, not as claims that every change corresponds to a specific Git revert commit.

---

# Testing and AI benchmarking

A strategy game can look correct on screen while still containing subtle rule errors. Creator's testing work therefore focused on the game underneath the interface.

Important checks include legal movement within a dice roll, all eight directions, jumping, friendly-occupied destinations, captures and returns, turn progression, pattern targeting, complete-formation victory, and AI legality.

Fairness was also a recurring concern. BLUE and RED should be governed by the same rules; AI strength should not be confused with a hidden advantage in dice generation or movement legality.

AI comparisons use repeatable testing where possible, including controlled seeds and paired conditions. Those experiments are useful for finding regressions and comparing agents, but they should not be mistaken for a claim that a particular AI is unbeatable or that BLUE and RED have identical empirical win rates in every sample.

Run the available test suite with:

```bash
python -m pytest -q
```

A benchmark that stops after a configured number of turns has reached an **experimental cutoff**, not an in-game victory. This distinction is important when interpreting AI results.

---

# Running Creator locally

Clone the repository:

```bash
git clone https://github.com/dkconnect/Creator.git
cd Creator
```

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the browser edition locally:

```bash
python web_server.py
```

Open **http://localhost:8000/**.

To run the desktop/Pygame edition, use the desktop entry point provided by the checked-out repository. The web server is a separate entry point and does not launch the desktop window.

---

# Public deployment

The browser edition is hosted on **[Render](https://render.com/)**:

**https://creator-game.onrender.com/**

Render runs the Python server and serves the HTML, CSS, and JavaScript frontend from the same application. This avoids a separate frontend/backend deployment and keeps the browser requests on one origin.

Each visitor receives an independent session and game instance. Session state is currently stored in server memory rather than a database. This keeps the architecture lightweight, but it has practical consequences: a restart or redeploy can end ongoing games, and the free instance may take time to wake after inactivity.

The current public edition is intended for individual visitors playing locally or against AI, **not** for networked human-versus-human matches.

---

# Project journey

The major development phases, in order, were:

| Phase | Focus | Outcome |
| --- | --- | --- |
| Initial prototype | Browser/JavaScript board concept | Established the formation-game idea |
| Python transition | Modular game state and Pygame | Centralized rules and desktop play |
| Engine refinement | Movement, captures, respawns, victory | Stable current rule set |
| AI development | Basic, Learning, Advanced | Three Python opponents |
| Dice seperation | Dice isolation and symmetry | AI does not influence rolls |
| Benchmarks | AI benchmarks | Repeatable comparative testing |
| Release | Release/regression checks | Stronger gameplay invariants |
| Server | Python web server | Browser access to the engine |
| Interface | Web visual redesign | Dark tactical interface |
| AI Integration | Web AI integration | AI modes in the browser |
| Interface B | Home/game split | Pattern selection before the board; better fit |
| Polish | Interface polish | Rulebook link, footer, responsive controls |
| Deployment | Render deployment | Public HTTPS game |

These are **development milestones**, not a fabricated list of Git commits. The repository's actual commit history is the authoritative record of individual code changes.

The next planned release task is packaging the desktop edition as a Windows executable. Documentation and the official rulebook are being prepared alongside the public web release.

---

# Design review

## What worked

**The formation objective.** It gives Creator a different strategic focus from elimination-based board games. A capture matters because of the squares it opens, protects, or denies.

**A single Python rules engine.** Movement, dice, AI, and victory checks do not have to be independently rewritten for the browser.

**Dice as a constraint rather than an instruction.** The player can make meaningful positional decisions even after receiving a random roll.

**Multiple AI agents.** Different opponents create a useful environment for both play and testing.

**The two-screen browser layout.** Moving setup away from the board made the 16 × 16 play area easier to use on limited screen space.

## What needed correction

**Rule drift.** Early versions and descriptions did not always agree on exact-distance movement, victory thresholds, or player roles. The final rules had to be explicitly fixed and tested.

**Artificial benchmark endings.** Experimental timeouts needed to remain separate from real match outcomes.

**UI scale.** A large board that technically renders is not necessarily a board that fits a laptop screen. The layout needed to respond to viewport height, not only width.

**Public hosting state.** In-memory sessions are straightforward and sufficient for an initial release, but they do not provide permanent match persistence.

---

# Known limitations

Creator is an actively developed independent game project. The current version has several practical limits:

- The public Render service may sleep when idle, causing a cold-start delay.
- Browser matches are stored in memory and can be lost on server restart or redeployment.
- Human vs Human on the website is local turn-taking, not online multiplayer.
- Some formations may produce long matches; the game intentionally has no forced turn limit.
- The AI agents are implemented opponents, not a guarantee of optimal play.
- The desktop Windows executable is a planned packaging step, not yet part of the current web release.

These limits are part of the present design rather than features the project claims to have solved.

---

# Roadmap

The immediate priorities are to finish publishing the standalone official rulebook, keep the public browser build stable, and package the desktop version for Windows.

Longer-term improvements may include more comprehensive AI evaluation, improved match persistence, accessibility refinements, and additional presentation features. Online multiplayer is **not** part of the current release plan.

---

# What building Creator taught me

The largest shift in this project was from thinking of a game as a board on a screen to thinking of it as a set of **precise, testable rules**.

A move is not just an animation. It is a question of turn ownership, dice limits, direction, destination occupancy, captures, and what the resulting board means for victory. An AI is not just something that picks a square. It must operate under exactly the same rules as the human player. A web interface is not a second implementation of the game; it is another way to interact with the same engine.

Several early ideas were revised or dropped. That is part of the project's history. The goal was not to preserve the first implementation unchanged, but to make the rules consistent, the architecture understandable, and the game playable beyond the development machine.

Creator is now a complete playable concept with a Python core and a public browser edition. There is still room to improve its AI, documentation, packaging, and hosting, but the central idea remains the same:

> **Win by creating the formation.**

---

<div align="center">

**CREATOR**

*Designed and developed by [Dibyanshu Kumar](https://github.com/dkconnect).*

**[Play the game](https://creator-game.onrender.com/) · [View the source](https://github.com/dkconnect/Creator)**

</div>
