<div align="center">

# CREATOR
### *A Pattern of Mind. A War of Memory.*

[![Live Game](https://img.shields.io/badge/Live_Game-Vercel-8B5CF6?style=for-the-badge&logo=vercel)](https://creator-dun.vercel.app)
[![Tech Stack](https://img.shields.io/badge/Tech_Stack-JS_Module_|_Canvas_2D_|_Tailwind-D4AF37?style=for-the-badge)](#-tech-stack--architecture)
[![License: MIT](https://img.shields.io/badge/License-MIT-000000.svg?style=for-the-badge)](LICENSE)

An original, asymmetric, stochastic adversarial board game played on a $16 \times 16$ lattice. One player (the **Creator**) attempts to reconstruct a memorized target pattern, while the opposing player (the **Destroyer**) seeks to obstruct, capture, and corrupt the spatial layout.

<br />

<table align="center">
    <thead>
        <tr>
            <th>Role</th>
            <th>Primary Objective</th>
            <th>Win Condition</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><b>Creator (C)</b></td>
            <td>Spatial Pattern Reconstruction</td>
            <td>Occupy all required $7 \times 7$ pattern cells simultaneously</td>
        </tr>
        <tr>
            <td><b>Destroyer (D)</b></td>
            <td>Adversarial Disruption & Occupation</td>
            <td>Block, capture, and prevent Creator completion</td>
        </tr>
    </tbody>
</table>

</div>

---

## Game Overview & Mechanics

**CREATOR** blends spatial pattern recognition, stochastic discrete movement, and tactical combat into a unique competitive experience.

### 1. Board & Initial State
* **Board Lattice ($\mathcal{B}$):** A $16 \times 16$ discrete grid ($256$ cells).
* **Target Matrix ($P$):** A $7 \times 7$ binary pattern matrix centered on the board ($P \in \{0,1\}^{7\times7}$).
* **Starting Setup:**
  * **Creator Pawns ($C$):** Fill the top two rows (32 pawns total).
  * **Destroyer Pawns ($D$):** Fill the bottom two rows (32 pawns total).

### 2. Pattern Preview Phase
Before gameplay begins, the board displays the chosen target pattern (Alphabets A–Z, Numbers 0–9, Symbols, or Custom Shapes) centered on the grid. After a short preview, the pattern fades into memory, requiring the Creator to build under cognitive uncertainty while the Destroyer predicts and blocks potential completion paths.

### 3. Stochastic 8-Directional Movement
On each turn, the active player:
1. **Rolls a 6-sided die** ($d \in \{1, 2, 3, 4, 5, 6\}$).
2. Selects a pawn at position $(r, c)$.
3. Moves the pawn **exactly** $d$ units in one of the 8 grid directions:

$$\Delta \in \{( \pm 1, 0), (0, \pm 1), (\pm 1, \pm 1)\}$$

$$(r', c') = (r + d \cdot \Delta_r, c + d \cdot \Delta_c)$$

### 4. Capture & Respawn
If a pawn lands on a cell occupied by an opponent's pawn, the opponent's pawn is captured and immediately returned to an empty cell in its home spawn region. No pawns are permanently eliminated.

---

## Mathematical Formulation

The game state is defined as a tuple:

$$\mathcal{G} = \left( \mathcal{S}, P', t, d \right)$$

where:
* $\mathcal{S} \in \{\emptyset, C, D\}^{16 \times 16}$ represents the spatial cell ownership.
* $P' \in \{0,1\}^{16 \times 16}$ is the centered, embedded $7 \times 7$ target pattern.
* $t \in \{C, D\}$ is the current turn player.
* $d \sim \text{Uniform}(\{1, 2, 3, 4, 5, 6\})$ represents the exogenous dice value.

### Victory Constraint
The Creator wins immediately at step $k$ if:

$$\forall (i, j) \in \mathcal{B}, \quad P'_{i,j} = 1 \implies \mathcal{S}_{i,j} = C$$

### AI Heuristic Model
When running in AI mode, the heuristic utility function evaluates candidate moves using:

$$U(m) = \alpha C_p + \beta R - \gamma O_p + \delta D$$

* $C_p$: Occupation / control of target pattern cells
* $R$: Opponent capture value
* $O_p$: Opponent pattern completion progress
* $D$: Disruption and tactical blocking potential

---

## Tech Stack & Architecture

* **UI Layer:** HTML5, CSS Glassmorphism, Tailwind CSS, Google Fonts (*Cinzel Decorative*, *Montserrat*)
* **Rendering Engine:** HTML5 Canvas2D Context (High-frequency 60 FPS requestAnimationFrame loop)
* **Modular JavaScript Architecture:**
  * `ui.js`: Handles start menu configuration, category filters, and localStorage persistence.
  * `patterns.js`: Contains $7 \times 7$ binary matrix definitions for letters, numbers, and shapes.
  * `game.js`: Core game loop, 8-directional move validation, canvas drawing, and turn state management.

---

## Repository
```
.
├── index.html     # Start screen, role selection & pattern picker
├── style.css      # Dark luxury glassmorphism styles & neon overlays
├── ui.js          # Menu controller & game config setup
├── game.html      # Main gameplay UI & canvas viewport
├── game.css       # Game UI layout & color definitions
├── patterns.js    # 7x7 matrix definitions (A-Z, 0-9, shapes)
└── game.js        # Core game engine, movement rules & canvas renderer
```

---

## Running Locally
```
1. Clone the repository:
    git clone [https://github.com/dkconnect/creator-game.git](https://github.com/dkconnect/creator-game.git)
    cd creator-game
    Serve using any standard static HTTP server:

Using Python 3
python -m http.server 8000
Open in browser: Navigate to http://localhost:8000 in your web browser.
```

---


## Rulebook Summary
* Turn Sequence: Roll Dice → Select Pawn → Move Exact Distance → End Turn.
* Partial Movements: Not allowed. Moves must equal the exact dice roll distance.
* Friendly Stacking: Invalid. You cannot land on a cell occupied by a friendly pawn.
* Winning: Creator wins the moment all active pattern cells are filled with C pawns. Extra C pawns outside the pattern do not invalidate victory.

---
<div align="center">
Created & Invented by Dibyanshu 
