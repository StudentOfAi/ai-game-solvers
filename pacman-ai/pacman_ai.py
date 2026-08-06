#!/usr/bin/env python3
"""
Pac-Man AI — A* Pathfinding + Ghost State Machines with GUI

Autonomous 0-player game with tkinter canvas:
  - Pac-Man uses A* to find nearest dot
  - Ghosts use Chase/Scatter/Frightened state machines
  - BFS navigation for ghost pathfinding

Clone and run: python3 pacman_ai.py
"""

import heapq
import random
import tkinter as tk
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

# Colors
BG = "#000000"
WALL = "#1a1a4a"
DOT = "#ffdd44"
PACMAN = "#ffee00"
BLINKY = "#ff0000"
PINKY = "#ff7777"
FRIGHTENED = "#4444ff"
EMPTY = "#0a0a0a"

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
    CHASE = 1
    SCATTER = 2
    FRIGHTENED = 3


@dataclass
class Pos:
    row: int
    col: int
    def __eq__(self, o): return self.row == o.row and self.col == o.col
    def __hash__(self): return hash((self.row, self.col))
    def __lt__(self, o): return (self.row, self.col) < (o.row, o.col)


class Maze:
    def __init__(self):
        self.rows = len(MAZE_TEMPLATE)
        self.cols = max(len(r) for r in MAZE_TEMPLATE)
        self.grid = []
        for line in MAZE_TEMPLATE:
            self.grid.append(list(line.ljust(self.cols)))
        self.dots = sum(1 for row in self.grid for c in row if c == '.')

    def is_wall(self, r, c):
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return True
        return self.grid[r][c] == '#'

    def has_dot(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == '.'

    def eat_dot(self, r, c):
        if self.has_dot(r, c):
            self.grid[r][c] = ' '
            self.dots -= 1


class PacmanAI:
    def __init__(self, start, maze):
        self.pos = start
        self.maze = maze
        self.score = 0

    def move(self, ghosts):
        target = self._nearest_dot()
        if not target:
            return
        path = self._astar(self.pos, target)
        if path and len(path) > 1:
            nxt = path[1]
            ghost_pos = {g.pos for g in ghosts if g.state != GhostState.FRIGHTENED}
            if nxt in ghost_pos:
                alts = self._valid_moves(self.pos)
                safe = [m for m in alts if m not in ghost_pos]
                if safe:
                    nxt = safe[0]
            self.pos = nxt
            if self.maze.has_dot(self.pos.row, self.pos.col):
                self.maze.eat_dot(self.pos.row, self.pos.col)
                self.score += 10

    def _nearest_dot(self):
        q = deque([(self.pos, 0)])
        seen = {self.pos}
        while q:
            pos, d = q.popleft()
            if self.maze.has_dot(pos.row, pos.col):
                return pos
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                np = Pos(pos.row+dr, pos.col+dc)
                if not self.maze.is_wall(np.row, np.col) and np not in seen:
                    seen.add(np)
                    q.append((np, d+1))
        return None

    def _astar(self, start, goal):
        open_set = [(0, start)]
        came = {}
        g = {start: 0}
        while open_set:
            _, cur = heapq.heappop(open_set)
            if cur == goal:
                path = [cur]
                while cur in came:
                    cur = came[cur]
                    path.append(cur)
                return list(reversed(path))
            for nb in self._valid_moves(cur):
                tg = g[cur] + 1
                if nb not in g or tg < g[nb]:
                    came[nb] = cur
                    g[nb] = tg
                    h = abs(nb.row - goal.row) + abs(nb.col - goal.col)
                    heapq.heappush(open_set, (tg + h, nb))
        return []

    def _valid_moves(self, pos):
        moves = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = pos.row+dr, pos.col+dc
            if not self.maze.is_wall(nr, nc):
                moves.append(Pos(nr, nc))
        return moves


@dataclass
class Ghost:
    name: str
    pos: Pos
    state: GhostState = GhostState.SCATTER
    scatter_target: Pos = field(default_factory=lambda: Pos(0, 0))
    timer: int = 0

    def move(self, maze, pacman):
        self.timer -= 1
        if self.state == GhostState.CHASE and self.timer <= 0:
            self.state = GhostState.SCATTER
            self.timer = 10
        elif self.state == GhostState.SCATTER and self.timer <= 0:
            self.state = GhostState.CHASE
            self.timer = 20
        elif self.state == GhostState.FRIGHTENED and self.timer <= 0:
            self.state = GhostState.CHASE
            self.timer = 20

        if self.state == GhostState.FRIGHTENED:
            moves = self._valid(maze)
            if moves:
                self.pos = random.choice(moves)
        elif self.state == GhostState.SCATTER:
            path = self._bfs(maze, self.pos, self.scatter_target)
            if path and len(path) > 1:
                self.pos = path[1]
        else:
            target = pacman if self.name == "Blinky" else Pos(max(0, pacman.row-4), pacman.col)
            path = self._bfs(maze, self.pos, target)
            if path and len(path) > 1:
                self.pos = path[1]

    def _valid(self, maze):
        moves = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = self.pos.row+dr, self.pos.col+dc
            if not maze.is_wall(nr, nc):
                moves.append(Pos(nr, nc))
        return moves

    def _bfs(self, maze, start, goal):
        q = deque([[start]])
        seen = {start}
        while q:
            path = q.popleft()
            cur = path[-1]
            if cur == goal:
                return path
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                np = Pos(cur.row+dr, cur.col+dc)
                if not maze.is_wall(np.row, np.col) and np not in seen:
                    seen.add(np)
                    q.append(path + [np])
        return []


class PacmanGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pac-Man AI — A* Pathfinding + Ghost State Machines")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        tk.Label(self.root, text="Pac-Man AI", font=("Helvetica", 16, "bold"),
                 fg=PACMAN, bg=BG).pack(pady=5)
        tk.Label(self.root, text="A* Navigation · Ghost Chase/Scatter/Frightened",
                 font=("Helvetica", 10), fg="#888888", bg=BG).pack()

        self.info = tk.Frame(self.root, bg=BG)
        self.info.pack(pady=5, padx=10, fill="x")
        self.tick_label = tk.Label(self.info, text="Tick: 0", font=("Courier", 11),
                                   fg="#e0e0e0", bg=BG)
        self.tick_label.pack(side="left", padx=5)
        self.score_label = tk.Label(self.info, text="Score: 0", font=("Courier", 11),
                                    fg=DOT, bg=BG)
        self.score_label.pack(side="left", padx=5)
        self.status_label = tk.Label(self.info, text="Playing...", font=("Courier", 11),
                                     fg=PACMAN, bg=BG)
        self.status_label.pack(side="right", padx=5)

        self.cell = 24
        self.maze = Maze()
        self.pacman = PacmanAI(Pos(7, 9), self.maze)
        self.ghosts = [
            Ghost("Blinky", Pos(1, 1), GhostState.SCATTER, Pos(0, 0), 10),
            Ghost("Pinky", Pos(1, 17), GhostState.SCATTER, Pos(0, 18), 10),
        ]
        self.tick = 0
        self.game_over = False
        self.won = False

        w = self.maze.cols * self.cell
        h = self.maze.rows * self.cell
        self.canvas = tk.Canvas(self.root, width=w, height=h, bg=BG, highlightthickness=0)
        self.canvas.pack(padx=10, pady=5)

        tk.Label(self.root, text="SPACE: next tick · A: auto-play · R: reset",
                 font=("Helvetica", 9), fg="#444444", bg=BG).pack(pady=3)

        self.root.bind("<space>", lambda e: self.step())
        self.root.bind("a", lambda e: self.auto_play())
        self.root.bind("r", lambda e: self.reset())

        self.draw()
        self.root.after(500, self.auto_play)

    def draw(self):
        self.canvas.delete("all")
        for r in range(self.maze.rows):
            for c in range(self.maze.cols):
                ch = self.maze.grid[r][c]
                x1 = c * self.cell
                y1 = r * self.cell
                x2 = x1 + self.cell
                y2 = y1 + self.cell
                pos = Pos(r, c)

                if ch == '#':
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=WALL, outline="#2a2a5a")
                elif ch == '.':
                    self.canvas.create_oval(x1+self.cell//2-2, y1+self.cell//2-2,
                                           x1+self.cell//2+2, y1+self.cell//2+2, fill=DOT)
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=EMPTY, outline="")

                # Draw Pac-Man
                if pos == self.pacman.pos:
                    cx, cy = x1 + self.cell//2, y1 + self.cell//2
                    self.canvas.create_oval(cx-8, cy-8, cx+8, cy+8, fill=PACMAN, outline="")

                # Draw Ghosts
                for g in self.ghosts:
                    if g.pos == pos:
                        cx, cy = x1 + self.cell//2, y1 + self.cell//2
                        color = FRIGHTENED if g.state == GhostState.FRIGHTENED else (BLINKY if g.name == "Blinky" else PINKY)
                        self.canvas.create_oval(cx-8, cy-8, cx+8, cy+8, fill=color, outline="")
                        # Eyes
                        self.canvas.create_oval(cx-4, cy-4, cx-2, cy-2, fill="white")
                        self.canvas.create_oval(cx+2, cy-4, cx+4, cy-2, fill="white")

        self.root.update()

    def step(self):
        if self.game_over or self.won:
            return
        self.tick += 1
        self.pacman.move(self.ghosts)
        for g in self.ghosts:
            g.move(self.maze, self.pacman.pos)

        # Collision
        for g in self.ghosts:
            if g.pos == self.pacman.pos:
                if g.state == GhostState.FRIGHTENED:
                    g.state = GhostState.CHASE
                    g.timer = 20
                    g.pos = g.scatter_target
                    self.pacman.score += 200
                else:
                    self.game_over = True
                    self.draw()
                    self.status_label.config(text=f"💀 Caught by {g.name}!", fg=BLINKY)
                    return

        if self.maze.dots == 0:
            self.won = True
            self.draw()
            self.status_label.config(text="🎉 ALL DOTS EATEN!", fg=DOT)
            return

        self.tick_label.config(text=f"Tick: {self.tick}")
        self.score_label.config(text=f"Score: {self.pacman.score}")
        self.draw()

    def auto_play(self):
        if self.game_over or self.won:
            return
        self.step()
        if not self.game_over and not self.won:
            self.root.after(200, self.auto_play)

    def reset(self):
        self.maze = Maze()
        self.pacman = PacmanAI(Pos(7, 9), self.maze)
        self.ghosts = [
            Ghost("Blinky", Pos(1, 1), GhostState.SCATTER, Pos(0, 0), 10),
            Ghost("Pinky", Pos(1, 17), GhostState.SCATTER, Pos(0, 18), 10),
        ]
        self.tick = 0
        self.game_over = False
        self.won = False
        self.tick_label.config(text="Tick: 0")
        self.score_label.config(text="Score: 0")
        self.status_label.config(text="Playing...", fg=PACMAN)
        self.draw()
        self.root.after(500, self.auto_play)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    random.seed(42)
    app = PacmanGUI()
    app.run()
