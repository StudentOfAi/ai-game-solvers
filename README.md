# AI Game Solvers

Autonomous (0-player) game solvers — all browser-based, zero dependencies.
Live demos below — click to play instantly, no clone required.

## Live Interactive Demos

| Solver | Algorithm | Live Demo |
|--------|-----------|-----------|
| Minesweeper | CSP + Probability | [▶ Play](https://studentofai.github.io/ai-game-solvers/minesweeper-solver/) |
| Pac-Man | A* + Ghost FSM | [▶ Play](https://studentofai.github.io/ai-game-solvers/pacman-ai/) |
| Word Search | 8-Directional Scan | [▶ Play](https://studentofai.github.io/ai-game-solvers/wordsearch-solver/) |
| HTML Snake | BFS + Flood-fill | [▶ Play](https://studentofai.github.io/ai-game-solvers/html-snake-engine/) |

## Solvers

### Minesweeper — CSP + Probability Engine
**Play:** https://studentofai.github.io/ai-game-solvers/minesweeper-solver/

Canvas grid auto-plays minesweeper:
- **Constraint propagation:** If cell's number equals flagged neighbors, remaining are safe
- **Mine inference:** Remaining unrevealed cells equal mine count → all flagged
- **Probability fallback:** Picks lowest-risk cell when no deterministic move exists

Controls: SOLVE (auto-play) · NEW GAME (reset)

### Pac-Man — A* Pathfinding & Ghost State Machines
**Play:** https://studentofai.github.io/ai-game-solvers/pacman-ai/

Canvas maze with Pac-Man auto-navigating:
- **A* pathfinding:** Finds nearest dot with Manhattan distance heuristic
- **Ghost AI:** Chase (target Pac-Man) / Scatter (corner retreat)
- **Blinky:** Direct chase · **Pinky:** 4-tile ambush

Controls: PLAY/PAUSE · RESET

### Word Search — 8-Directional Matrix Scanner
**Play:** https://studentofai.github.io/ai-game-solvers/wordsearch-solver/

Canvas letter grid with 10 categories (200 words total):
- **8-directional scanning:** N, NE, E, SE, S, SW, W, NW
- **Word highlighting:** Found words highlighted in distinct colors
- **Categories:** Animals, Space, Food & Drinks, Technology, Movies, Sports, Science, Nature, Music, Travel
- **Live word list:** Crossed out as found

Controls: Click category to switch · NEW PUZZLE · SOLVE

### HTML Snake — BFS Pathfinding & Canvas State Mechanics
**Play:** https://studentofai.github.io/ai-game-solvers/html-snake-engine/

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

# All games open in any browser — no dependencies:
open minesweeper-solver/index.html
open pacman-ai/index.html
open wordsearch-solver/index.html
open html-snake-engine/index.html
```

Or just play online: https://studentofai.github.io/ai-game-solvers/

## Requirements

- Any modern browser (Chrome, Safari, Firefox, Edge)
- No build step, no server, no dependencies — pure HTML5 + Canvas + vanilla JS

## Architecture

```
ai-game-solvers/
├── minesweeper-solver/
│   ├── index.html              — CSP + probability, canvas grid
│   └── icon.png                — Game screenshot icon
├── pacman-ai/
│   ├── index.html              — A* + ghost FSM, canvas maze
│   └── icon.png                — Game screenshot icon
├── wordsearch-solver/
│   ├── index.html              — 8-directional scanner, 10 categories, 200 words
│   └── icon.png                — Game screenshot icon
├── html-snake-engine/
│   ├── index.html              — BFS pathfinding, canvas rendering, Web Audio
│   └── icon.png                — Game screenshot icon
├── minesweeper-solver/minesweeper_solver.py  — Legacy Python (tkinter, requires macOS fix)
├── pacman-ai/pacman_ai.py                    — Legacy Python (tkinter, requires macOS fix)
├── wordsearch-solver/wordsearch_solver.py   — Legacy Python (tkinter, requires macOS fix)
├── LICENSE
├── README.md
└── requirements.txt
```

## Algorithms

| Solver | Algorithm | Key Technique |
|--------|-----------|---------------|
| Minesweeper | CSP + Probability | Constraint propagation, mine inference, flood fill |
| Pac-Man | A* + State Machines | Manhattan heuristic, BFS ghost navigation, FSM transitions |
| Word Search | 8-Directional Scan | Grid generation, directional string matching, word highlighting |
| HTML Snake | BFS + Flood-fill | Shortest-path to food, open-space survival heuristic, canvas rendering |

## License

MIT
