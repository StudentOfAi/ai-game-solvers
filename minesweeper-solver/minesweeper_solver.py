#!/usr/bin/env python3
"""
Minesweeper Solver — CSP + Probability Engine with GUI

Autonomous 0-player solver with tkinter GUI that pops up on launch.
Clone and run: python3 minesweeper_solver.py

Algorithms:
  - Constraint propagation (safe/mine inference from revealed numbers)
  - Probability estimation for non-deterministic moves
  - Flood fill for zero-adjacency cells
"""

import random
import tkinter as tk
from tkinter import font
from dataclasses import dataclass
from typing import Optional
import time

# Colors
COVERED = "#3a3a4a"
COVERED_HL = "#5a5a7a"
REVEALED = "#1a1a2a"
MINE_COLOR = "#ff4444"
FLAG_COLOR = "#ffaa00"
SAFE_COLOR = "#44ff44"
PROB_COLOR = "#ff8800"
BG = "#0d0d1a"
TEXT_LIGHT = "#e0e0e0"
NUM_COLORS = {0: "#666666", 1: "#4488ff", 2: "#44ff44", 3: "#ff4444",
              4: "#ff44ff", 5: "#ffff44", 6: "#44ffff", 7: "#ff8800", 8: "#ffffff"}


@dataclass
class Cell:
    is_mine: bool = False
    is_revealed: bool = False
    is_flagged: bool = False
    adjacent: int = 0
    row: int = 0
    col: int = 0


class MinesweeperBoard:
    def __init__(self, rows=10, cols=10, mines=12):
        self.rows = rows
        self.cols = cols
        self.mine_count = mines
        self.grid: list[list[Cell]] = []
        self._generate()

    def _generate(self):
        self.grid = [[Cell(row=r, col=c) for c in range(self.cols)] for r in range(self.rows)]
        positions = random.sample(range(self.rows * self.cols), self.mine_count)
        for pos in positions:
            r, c = pos // self.cols, pos % self.cols
            self.grid[r][c].is_mine = True
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c].is_mine:
                    self.grid[r][c].adjacent = self._count_adj(r, c)

    def _count_adj(self, r, c):
        cnt = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc].is_mine:
                    cnt += 1
        return cnt

    def reveal(self, r, c) -> bool:
        cell = self.grid[r][c]
        if cell.is_flagged or cell.is_revealed:
            return True
        if cell.is_mine:
            cell.is_revealed = True
            return False
        cell.is_revealed = True
        if cell.adjacent == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal(nr, nc)
        return True

    def flag(self, r, c):
        self.grid[r][c].is_flagged = True

    def get_neighbors(self, r, c):
        result = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    result.append(self.grid[nr][nc])
        return result

    def is_won(self):
        for row in self.grid:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return False
        return True


class MinesweeperSolver:
    def __init__(self, board):
        self.board = board
        self.move_count = 0

    def next_move(self) -> Optional[tuple]:
        """Returns (row, col, action) where action is 'reveal' or 'flag', or None if stuck."""
        # Constraint propagation first
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.grid[r][c]
                if not cell.is_revealed or cell.adjacent == 0:
                    continue
                neighbors = self.board.get_neighbors(r, c)
                flagged = sum(1 for n in neighbors if n.is_flagged)
                unrevealed = [n for n in neighbors if not n.is_revealed and not n.is_flagged]
                if not unrevealed:
                    continue
                # Safe inference
                if cell.adjacent == flagged:
                    n = unrevealed[0]
                    return (n.row, n.col, "reveal")
                # Mine inference
                if cell.adjacent - flagged == len(unrevealed):
                    n = unrevealed[0]
                    return (n.row, n.col, "flag")

        # Probability fallback
        best_prob = 1.0
        best_cell = None
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.grid[r][c]
                if cell.is_revealed or cell.is_flagged:
                    continue
                prob = self._estimate(r, c)
                if prob < best_prob:
                    best_prob = prob
                    best_cell = (r, c)
        if best_cell:
            return (best_cell[0], best_cell[1], "reveal")
        return None

    def _estimate(self, r, c):
        constraints = []
        for n in self.board.get_neighbors(r, c):
            if n.is_revealed and n.adjacent > 0:
                flagged = sum(1 for nn in self.board.get_neighbors(n.row, n.col) if nn.is_flagged)
                unrev = [nn for nn in self.board.get_neighbors(n.row, n.col) if not nn.is_revealed and not nn.is_flagged]
                if unrev:
                    constraints.append((n.adjacent - flagged) / len(unrev))
        if constraints:
            return max(constraints)
        total_mines = self.board.mine_count
        unrevealed = sum(1 for row in self.board.grid for cell in row if not cell.is_revealed and not cell.is_flagged)
        return total_mines / max(unrevealed, 1)


class MinesweeperGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Minesweeper CSP Solver — 0-Player Autonomous")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(pady=5)
        tk.Label(header, text="Minesweeper Solver", font=("Helvetica", 16, "bold"),
                 fg="#ffffff", bg=BG).pack()
        tk.Label(header, text="CSP + Probability Engine", font=("Helvetica", 10),
                 fg=TEXT_LIGHT, bg=BG).pack()

        # Info bar
        self.info_frame = tk.Frame(self.root, bg=BG)
        self.info_frame.pack(pady=5, padx=10, fill="x")
        self.move_label = tk.Label(self.info_frame, text="Move: 0", font=("Courier", 11),
                                   fg=TEXT_LIGHT, bg=BG)
        self.move_label.pack(side="left", padx=5)
        self.status_label = tk.Label(self.info_frame, text="Solving...", font=("Courier", 11),
                                     fg=SAFE_COLOR, bg=BG)
        self.status_label.pack(side="right", padx=5)

        # Game setup
        self.board = MinesweeperBoard(10, 10, 12)
        self.solver = MinesweeperSolver(self.board)
        self.move_count = 0
        self.game_over = False

        # Cell size
        self.cell_size = 32

        # Grid canvas
        canvas_w = self.board.cols * self.cell_size
        canvas_h = self.board.rows * self.cell_size
        self.canvas = tk.Canvas(self.root, width=canvas_w, height=canvas_h, bg=BG, highlightthickness=0)
        self.canvas.pack(padx=10, pady=5)

        # Legend
        legend = tk.Frame(self.root, bg=BG)
        legend.pack(pady=5)
        items = [("Covered", COVERED), ("Safe", SAFE_COLOR), ("Mine", MINE_COLOR), ("Flag", FLAG_COLOR)]
        for label, color in items:
            box = tk.Label(legend, text="  ", bg=color, width=2, height=1)
            box.pack(side="left", padx=2)
            tk.Label(legend, text=label, fg=TEXT_LIGHT, bg=BG, font=("Helvetica", 9)).pack(side="left", padx=(2, 10))

        # Footer
        tk.Label(self.root, text="Press SPACE for next move · A for auto-play · R for new game",
                 font=("Helvetica", 9), fg="#666666", bg=BG).pack(pady=5)

        # Bind keys
        self.root.bind("<space>", lambda e: self.step())
        self.root.bind("a", lambda e: self.auto_play())
        self.root.bind("r", lambda e: self.reset())

        self.draw_grid()
        # Auto-start solving after 500ms
        self.root.after(500, self.auto_play)

    def draw_grid(self, highlight=None):
        self.canvas.delete("all")
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.grid[r][c]
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if highlight and highlight == (r, c):
                    bg = COVERED_HL
                    outline = SAFE_COLOR
                elif cell.is_flagged:
                    bg = COVERED
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                           text="🚩", font=("Helvetica", 14))
                elif not cell.is_revealed:
                    bg = COVERED
                elif cell.is_mine:
                    bg = MINE_COLOR
                else:
                    bg = REVEALED

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="#2a2a3a", width=1)

                if cell.is_revealed and not cell.is_mine and cell.adjacent > 0:
                    color = NUM_COLORS.get(cell.adjacent, "#ffffff")
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                           text=str(cell.adjacent),
                                           font=("Courier", 14, "bold"), fill=color)
                elif cell.is_revealed and cell.is_mine:
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                           text="💣", font=("Helvetica", 14))

        self.root.update()

    def step(self):
        if self.game_over:
            return
        move = self.solver.next_move()
        if move is None:
            self.status_label.config(text="No moves available", fg=PROB_COLOR)
            return

        r, c, action = move
        self.move_count += 1
        self.move_label.config(text=f"Move: {self.move_count}")

        if action == "reveal":
            success = self.board.reveal(r, c)
            if not success:
                self.game_over = True
                self.draw_grid(highlight=(r, c))
                self.status_label.config(text=f"💥 HIT MINE at ({r},{c}) — Game Over", fg=MINE_COLOR)
                return
        elif action == "flag":
            self.board.flag(r, c)
            self.status_label.config(text=f"⚑ Flagged ({r},{c}) — CSP mine inference", fg=FLAG_COLOR)

        self.draw_grid(highlight=(r, c))

        if self.board.is_won():
            self.game_over = True
            self.status_label.config(text=f"✅ SOLVED in {self.move_count} moves!", fg=SAFE_COLOR)

    def auto_play(self):
        if self.game_over:
            return
        self.step()
        if not self.game_over:
            self.root.after(150, self.auto_play)  # 150ms per move — watchable speed

    def reset(self):
        self.board = MinesweeperBoard(10, 10, 12)
        self.solver = MinesweeperSolver(self.board)
        self.move_count = 0
        self.game_over = False
        self.move_label.config(text="Move: 0")
        self.status_label.config(text="Solving...", fg=SAFE_COLOR)
        self.draw_grid()
        self.root.after(500, self.auto_play)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    random.seed(42)
    app = MinesweeperGUI()
    app.run()
