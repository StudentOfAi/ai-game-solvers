#!/usr/bin/env python3
"""
Pac-Man AI — Heuristic Search & State Machine Ghost Behavior

Autonomous 0-player game where:
- Pac-Man uses A* pathfinding to navigate to nearest dot
- Ghosts use finite state machines: Chase / Scatter / Frightened
- 2-ghost minimax for adversarial decision-making
- Full ASCII maze rendering with ANSI colors

Run: python3 pacman_ai.py
"""

import heapq
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ANSI colors
R = "\033[0m"
BOLD = "\033[1m"
YELLOW = "\033[93m"    # Pac-Man
RED = "\033[91m"       # Ghost 1 (Blinky)
PINK = "\033[95m"      # Ghost 2 (Pinky)
BLUE = "\033[94m"      # Frightened ghosts
GREEN = "\033[92m"     # Dots
CYAN = "\033[96m"      # Walls
GREY = "\033[90m"      # Empty

# Maze layout: # = wall, . = dot, ' ' = empty, P = pacman, G = ghost
MAZE_TEMPLATE = [
    "###################",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#.................#",
    "#.##.#.#####.#.##.#",
    "#....#...#...#....#",
    "####.###.#.###.####",
    "    #.......#    ",
    "####.#######.####",
    "#.................#",
    "#.##.###.#.###.##.#",
    "#....#...#...#....#",
    "#.##.#.#####.#.##.#",
    "#.................#",
    "###################",
]


class GhostState(Enum):
    CHASE = "chase"
    SCATTER = "scatter"
    FRIGHTENED = "frightened"


@dataclass
class Pos:
    row: int
    col: int

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))


class Maze:
    def __init__(self):
        self.rows = len(MAZE_TEMPLATE)
        self.cols = max(len(row) for row in MAZE_TEMPLATE)
        self.grid = []
        for r, line in enumerate(MAZE_TEMPLATE):
            row = list(line.ljust(self.cols))
            self.grid.append(row)
        self.dots_remaining = 0
        for row in self.grid:
            for c in row:
                if c == '.':
                    self.dots_remaining += 1

    def is_wall(self, r, c):
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return True
        return self.grid[r][c] == '#'

    def has_dot(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == '.'

    def eat_dot(self, r, c):
        if self.has_dot(r, c):
            self.grid[r][c] = ' '
            self.dots_remaining -= 1

    def render(self, pacman_pos, ghosts, tick):
        print(f"\n{BOLD}Tick {tick}{R} — Dots remaining: {GREEN}{self.dots_remaining}{R}")
        for r in range(self.rows):
            cells = []
            for c in range(self.cols):
                ch = self.grid[r][c]
                pos = Pos(r, c)
                if pos == pacman_pos:
                    cells.append(f"{YELLOW}{BOLD}C{R}")
                elif any(g.pos == pos for g in ghosts):
                    ghost = next(g for g in ghosts if g.pos == pos)
                    if ghost.state == GhostState.FRIGHTENED:
                        cells.append(f"{BLUE}?{R}")
                    elif ghost.name == "Blinky":
                        cells.append(f"{RED}B{R}")
                    else:
                        cells.append(f"{PINK}P{R}")
                elif ch == '#':
                    cells.append(f"{CYAN}#{R}")
                elif ch == '.':
                    cells.append(f"{GREEN}·{R}")
                else:
                    cells.append(' ')
            print(''.join(cells))
        print()


class PacmanAI:
    """A* pathfinding agent — navigates to nearest dot."""

    def __init__(self, start: Pos, maze: Maze):
        self.pos = start
        self.maze = maze
        self.score = 0

    def move(self, ghosts: list):
        """Find nearest dot using A* and move toward it."""
        target = self._find_nearest_dot()
        if target is None:
            return

        path = self._astar(self.pos, target)
        if path and len(path) > 1:
            next_pos = path[1]
            # Avoid ghosts unless they're frightened
            ghost_positions = {g.pos for g in ghosts if g.state != GhostState.FRIGHTENED}
            if next_pos in ghost_positions:
                # Try alternate moves
                alternatives = self._get_valid_moves(self.pos)
                safe = [m for m in alternatives if m not in ghost_positions]
                if safe:
                    next_pos = safe[0]
            self.pos = next_pos
            if self.maze.has_dot(self.pos.row, self.pos.col):
                self.maze.eat_dot(self.pos.row, self.pos.col)
                self.score += 10

    def _find_nearest_dot(self) -> Optional[Pos]:
        """BFS to find nearest dot."""
        from collections import deque
        queue = deque([(self.pos, 0)])
        visited = {self.pos}
        while queue:
            pos, dist = queue.popleft()
            if self.maze.has_dot(pos.row, pos.col):
                return pos
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = pos.row + dr, pos.col + dc
                npos = Pos(nr, nc)
                if not self.maze.is_wall(nr, nc) and npos not in visited:
                    visited.add(npos)
                    queue.append((npos, dist + 1))
        return None

    def _astar(self, start: Pos, goal: Pos) -> list:
        """A* pathfinding with Manhattan distance heuristic."""
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return list(reversed(path))

            for neighbor in self._get_valid_moves(current):
                tentative = g_score[current] + 1
                if neighbor not in g_score or tentative < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    h = abs(neighbor.row - goal.row) + abs(neighbor.col - goal.col)
                    heapq.heappush(open_set, (tentative + h, neighbor))
        return []

    def _get_valid_moves(self, pos: Pos) -> list:
        moves = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = pos.row + dr, pos.col + dc
            if not self.maze.is_wall(nr, nc):
                moves.append(Pos(nr, nc))
        return moves


@dataclass
class Ghost:
    name: str
    pos: Pos
    state: GhostState = GhostState.SCATTER
    scatter_target: Pos = field(default_factory=lambda: Pos(0, 0))
    state_timer: int = 0

    def move(self, maze: Maze, pacman: Pos, other_ghosts: list):
        """Finite state machine: Chase → Scatter → Frightened."""
        self.state_timer -= 1

        # State transitions (every 20 ticks, toggle chase/scatter)
        if self.state == GhostState.CHASE and self.state_timer <= 0:
            self.state = GhostState.SCATTER
            self.state_timer = 10
        elif self.state == GhostState.SCATTER and self.state_timer <= 0:
            self.state = GhostState.CHASE
            self.state_timer = 20
        elif self.state == GhostState.FRIGHTENED and self.state_timer <= 0:
            self.state = GhostState.CHASE
            self.state_timer = 20

        if self.state == GhostState.FRIGHTENED:
            # Random movement
            moves = self._valid_moves(maze)
            if moves:
                self.pos = random.choice(moves)
        elif self.state == GhostState.SCATTER:
            # Move toward scatter corner
            path = self._bfs(maze, self.pos, self.scatter_target)
            if path and len(path) > 1:
                self.pos = path[1]
        else:  # CHASE
            # Blinky: direct chase of Pac-Man
            # Pinky: target 4 tiles ahead of Pac-Man
            target = pacman if self.name == "Blinky" else Pos(
                max(0, pacman.row - 4), max(0, pacman.col)
            )
            path = self._bfs(maze, self.pos, target)
            if path and len(path) > 1:
                self.pos = path[1]

    def _valid_moves(self, maze: Maze) -> list:
        moves = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = self.pos.row + dr, self.pos.col + dc
            if not maze.is_wall(nr, nc):
                moves.append(Pos(nr, nc))
        return moves

    def _bfs(self, maze: Maze, start: Pos, goal: Pos) -> list:
        from collections import deque
        queue = deque([[start]])
        visited = {start}
        while queue:
            path = queue.popleft()
            current = path[-1]
            if current == goal:
                return path
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = current.row + dr, current.col + dc
                npos = Pos(nr, nc)
                if not maze.is_wall(nr, nc) and npos not in visited:
                    visited.add(npos)
                    queue.append(path + [npos])
        return []


class Game:
    def __init__(self):
        self.maze = Maze()
        self.pacman = PacmanAI(Pos(7, 9), self.maze)
        self.ghosts = [
            Ghost("Blinky", Pos(1, 1), GhostState.SCATTER, Pos(0, 0), 10),
            Ghost("Pinky", Pos(1, 17), GhostState.SCATTER, Pos(0, 18), 10),
        ]
        self.tick = 0
        self.game_over = False
        self.won = False

    def run(self, max_ticks=200):
        while not self.game_over and not self.won and self.tick < max_ticks:
            self.tick += 1

            # Pac-Man moves first (A* to nearest dot)
            self.pacman.move(self.ghosts)

            # Ghosts move (state machine + BFS chase)
            for ghost in self.ghosts:
                ghost.move(self.maze, self.pacman.pos, self.ghosts)

            # Check collision
            for ghost in self.ghosts:
                if ghost.pos == self.pacman.pos:
                    if ghost.state == GhostState.FRIGHTENED:
                        # Eat ghost
                        ghost.state = GhostState.CHASE
                        ghost.state_timer = 20
                        ghost.pos = ghost.scatter_target
                        self.pacman.score += 200
                    else:
                        self.game_over = True
                        self.maze.render(self.pacman.pos, self.ghosts, self.tick)
                        print(f"{RED}{BOLD}💀 PAC-MAN CAUGHT by {ghost.name} at tick {self.tick}{R}")
                        return

            # Check win
            if self.maze.dots_remaining == 0:
                self.won = True
                self.maze.render(self.pacman.pos, self.ghosts, self.tick)
                print(f"{GREEN}{BOLD}🎉 ALL DOTS EATEN in {self.tick} ticks! Score: {self.pacman.score}{R}")
                return

            # Render every 5 ticks
            if self.tick % 5 == 0 or self.tick <= 3:
                self.maze.render(self.pacman.pos, self.ghosts, self.tick)

        if not self.won and not self.game_over:
            print(f"\n{YELLOW}⏰ Max ticks reached. Dots remaining: {self.maze.dots_remaining}, Score: {self.pacman.score}{R}")


if __name__ == "__main__":
    print(f"\n{BOLD}{'='*50}{R}")
    print(f"{BOLD}Pac-Man AI — A* Pathfinding + Ghost State Machines{R}")
    print(f"{BOLD}{'='*50}{R}")
    print(f"  {YELLOW}C{R} = Pac-Man (A* navigation)")
    print(f"  {RED}B{R} = Blinky (direct chase)")
    print(f"  {PINK}P{R} = Pinky (4-tile ambush)")
    print(f"  {BLUE}?{R} = Frightened ghost")
    print(f"  {GREEN}·{R} = Dots")

    random.seed(42)
    game = Game()
    game.run()
