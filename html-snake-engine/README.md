# HTML Snake Engine

Browser-based state mechanics and lightweight canvas rendering — a single-file
HTML5 Snake game with a **0-Player AI Auto-Pilot Mode** using BFS pathfinding
to autonomously navigate to food.

## Architecture

```
index.html          ← Single-file game (canvas + vanilla JS, no dependencies)
  ├── Grid Engine        20×20 cell grid, collision detection, wall-wrap toggle
  ├── Canvas Renderer    640×640px <canvas> with gradient styling
  ├── State Machine       Stage progression (speed increases per stage)
  ├── Audio Engine        Procedural Web Audio beat track (kick/snare/hi-hat)
  └── AI Auto-Pilot       BFS pathfinding to nearest food, body-avoidance
```

## Modes

### Manual Mode (Human)
- Arrows / WASD to steer
- Esc: pause/resume
- End: toggle wall-wrap
- Home: restart
- M: mute audio

### 0-Player AI Auto-Pilot Mode
- Press `0` to toggle autonomous play
- BFS (Breadth-First Search) pathfinding computes the shortest path to the food
  each tick, avoiding the snake's own body
- When no safe path exists (surrounded by body), the auto-pilot falls back to the
  longest-survival direction (maximizes open space)
- Demonstrates graph traversal, real-time pathfinding, and collision avoidance
  in a constrained grid environment

## Technical Framing

This is a **state mechanics & graph traversal experiment**, not a tutorial:

- **State Management**: Immutable state transitions (new objects per tick, no mutation)
- **Grid-Based Pathfinding**: BFS over a 2D lattice with dynamic obstacle set (snake body)
- **Collision Detection**: O(1) occupancy set via `Set("x,y")` lookups
- **Render Loop**: requestAnimationFrame with accumulator-based fixed timestep
- **Procedural Audio**: Web Audio API oscillator + noise buffer synthesis
- **Stage Progression**: Exponential speed curve per stage — `speed = 2.5 + (stage-1) × 0.5`

## Run

```bash
# Clone the monorepo
git clone https://github.com/StudentOfAi/ai-game-solvers.git

# Open the game in any browser
open ai-game-solvers/html-snake-engine/index.html
```

No build step. No dependencies. No server. Pure HTML5 + Canvas + vanilla JS.

## Provenance

Originally built in Cursor IDE (~2 hours). Consolidated into ai-game-solvers
as an algorithmic engine experiment demonstrating browser-based state mechanics
and autonomous pathfinding.
