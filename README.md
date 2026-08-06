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

## Quick Start

```bash
git clone https://github.com/StudentOfAi/ai-game-solvers.git
cd ai-game-solvers

# Any of these pop up a window immediately:
python3 minesweeper-solver/minesweeper_solver.py
python3 pacman-ai/pacman_ai.py
python3 wordsearch-solver/wordsearch_solver.py
```

## Requirements

- Python 3.9+
- tkinter (included with macOS Python — no pip install needed)
- No external packages — pure stdlib

## Architecture

```
ai-game-solvers/
├── minesweeper-solver/
│   └── minesweeper_solver.py    — CSP + probability, tkinter canvas
├── pacman-ai/
│   └── pacman_ai.py             — A* + ghost FSM, tkinter canvas
├── wordsearch-solver/
│   └── wordsearch_solver.py     — KMP + brute-force, tkinter canvas
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

## License

MIT
