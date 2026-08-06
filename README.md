# AI Game Solvers

Autonomous (0-player) game solvers demonstrating constraint satisfaction, heuristic search, and string matching algorithms. No human input — the AI plays to completion.

## Solvers

### Minesweeper — Constraint Satisfaction Problem (CSP)
**Directory:** `minesweeper-solver/`

The AI evaluates safe moves vs probabilistic risks using logic rules:
- **Constraint propagation:** If a cell's number equals its flagged neighbors, remaining neighbors are safe
- **Mine inference:** If remaining unrevealed neighbors equal remaining mine count, all are mines
- **Probability estimation:** When no deterministic move exists, picks lowest-risk cell based on neighbor constraints and global mine density
- **Flood fill:** Zero-adjacency cells cascade reveal

```
Move #1: Reveal (5,5) — initial safe cell
Move #2: Reveal (4,4) — CSP safe (from 5,5)
  ⚑ Flagged (3,3) — CSP mine inference from (4,4)
✅ SOLVED in 33 moves
```

### Pac-Man — A* Pathfinding & Ghost State Machines
**Directory:** `pacman-ai/`

- **A\* pathfinding:** Pac-Man navigates to nearest dot using A* with Manhattan distance heuristic
- **Ghost state machines:** Chase / Scatter / Frightened modes with timed transitions
- **Blinky:** Direct chase (targets Pac-Man's position)
- **Pinky:** Ambush (targets 4 tiles ahead of Pac-Man)
- **BFS ghost navigation:** Ghosts use BFS to find paths to targets
- **Collision detection:** Pac-Man caught on ghost contact (unless frightened)

### Word Search — Matrix Manipulation & KMP String Matching
**Directory:** `wordsearch-solver/`

- **8-directional scanning:** N, NE, E, SE, S, SW, W, NW
- **Brute-force scan:** O(n × m × 8 × w) — check every cell, every direction
- **KMP (Knuth-Morris-Pratt):** O(n + m) per line — builds failure function, scans extracted direction lines
- **Performance benchmark:** Compares both approaches with nanosecond timing
- **Grid generation:** Words placed in random directions with overlap checking

## Architecture

```
ai-game-solvers/
├── minesweeper-solver/
│   └── minesweeper_solver.py    — CSP + probability engine
├── pacman-ai/
│   └── pacman_ai.py             — A* + ghost state machines
└── wordsearch-solver/
    └── wordsearch_solver.py     — KMP + brute-force comparison
```

## Run

```bash
python3 minesweeper-solver/minesweeper_solver.py
python3 pacman-ai/pacman_ai.py
python3 wordsearch-solver/wordsearch_solver.py
```

All solvers use ANSI colors for terminal rendering. No external dependencies — pure Python stdlib.

## Algorithms

| Solver | Algorithm | Complexity |
|--------|-----------|------------|
| Minesweeper | Constraint Satisfaction + Probability | O(cells × neighbors) per propagation pass |
| Pac-Man | A* with Manhattan heuristic | O(b^d) worst case, ~O(n) with good heuristic |
| Word Search (brute) | Naive directional scan | O(n × m × 8 × w) |
| Word Search (KMP) | Knuth-Morris-Pratt | O(n + m) per line per word |

## License

MIT — see [LICENSE](LICENSE)
