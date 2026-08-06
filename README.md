# AI Game Solvers

Autonomous (0-player) game solvers with GUI windows. Each solver pops up a window on launch — clone and run, no setup needed.

## Solvers

### Minesweeper — Constraint Satisfaction Problem (CSP)
**Run:** `python3 minesweeper-solver/minesweeper_solver.py`

GUI window pops up with a 10×10 grid. The solver auto-plays:
- **Constraint propagation:** If cell's number equals flagged neighbors, remaining are safe
- **Mine inference:** Remaining unrevealed cells equal mine count → all flagged
- **Probability fallback:** Picks lowest-risk cell when no deterministic move exists

Controls: SPACE (next move) · A (auto-play) · R (new game)

### Pac-Man — A* Pathfinding & Ghost State Machines
**Run:** `python3 pacman-ai/pacman_ai.py`

GUI window with ASCII maze. Pac-Man auto-navigates:
- **A\* pathfinding:** Finds nearest dot with Manhattan distance heuristic
- **Ghost AI:** Chase (target Pac-Man) / Scatter (corner retreat) / Frightened (random)
- **Blinky:** Direct chase · **Pinky:** 4-tile ambush

Controls: SPACE (next tick) · A (auto-play) · R (reset)

### Word Search — KMP String Matching
**Run:** `python3 wordsearch-solver/wordsearch_solver.py`

GUI window with 14×14 grid. Words revealed one at a time:
- **8-directional scanning:** N, NE, E, SE, S, SW, W, NW
- **Brute-force vs KMP benchmark:** Shows timing comparison
- **Color-coded results:** Each word highlighted in distinct color

Controls: R (new puzzle)

### HTML Snake — BFS Pathfinding & Canvas State Mechanics
**Run:** `open html-snake-engine/index.html`

Browser-based snake game with 0-player AI auto-pilot:
- **BFS pathfinding:** Shortest path to food each tick, body-avoidance
- **Flood-fill survival:** When no path to food, picks direction with most open space
- **Stage progression:** Exponential speed curve per stage
- **Procedural audio:** Web Audio API kick/snare/hi-hat synthesis

Controls: Arrows/WASD (move) · 0 (AI Auto-Pilot) · Esc (pause) · End (wrap) · Home (restart) · M (mute)

## Quick Start

```bash
git clone https://github.com/StudentOfAi/ai-game-solvers.git
cd ai-game-solvers

# Python solvers (pop up a window):
python3 minesweeper-solver/minesweeper_solver.py
python3 pacman-ai/pacman_ai.py
python3 wordsearch-solver/wordsearch_solver.py

# Browser-based snake (no dependencies):
open html-snake-engine/index.html
```

## Requirements

- Python 3.9+ (for minesweeper, pacman, wordsearch)
- tkinter (included with macOS Python — no pip install needed)
- Any modern browser (for HTML snake — no build step, no server)
- No external packages — pure stdlib + vanilla JS

## Architecture

```
ai-game-solvers/
├── minesweeper-solver/
│   └── minesweeper_solver.py    — CSP + probability, tkinter canvas
├── pacman-ai/
│   └── pacman_ai.py             — A* + ghost FSM, tkinter canvas
├── wordsearch-solver/
│   └── wordsearch_solver.py     — KMP + brute-force, tkinter canvas
├── html-snake-engine/
│   └── index.html               — BFS pathfinding, canvas rendering, Web Audio
├── LICENSE
├── README.md
└── requirements.txt
```

## Algorithms

| Solver | Algorithm | Key Technique |
|--------|-----------|---------------|
| Minesweeper | CSP + Probability | Constraint propagation, mine inference, flood fill |
| Pac-Man | A* + State Machines | Manhattan heuristic, BFS ghost navigation, FSM transitions |
| Word Search | KMP + Brute-force | Failure function, 8-directional line extraction, benchmark |
| HTML Snake | BFS + Flood-fill | Shortest-path to food, open-space survival heuristic, canvas rendering |

## License

MIT
