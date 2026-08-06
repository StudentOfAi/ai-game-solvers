#!/usr/bin/env python3
"""
Minesweeper Solver — Constraint Satisfaction Problem (CSP) & Probability Engine

Autonomous 0-player solver that applies:
1. Constraint propagation — if a cell's number equals flagged neighbors, remaining are safe
2. Probability estimation — when no deterministic move exists, pick lowest-risk cell
3. Auto-play loop — plays to completion without human input

Run: python3 minesweeper_solver.py
"""

import random
from dataclasses import dataclass, field
from typing import Optional

# ANSI colors
R = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
GREY = "\033[90m"


@dataclass
class Cell:
    is_mine: bool = False
    is_revealed: bool = False
    is_flagged: bool = False
    adjacent_mines: int = 0
    row: int = 0
    col: int = 0


class MinesweeperBoard:
    def __init__(self, rows=10, cols=10, mine_count=12):
        self.rows = rows
        self.cols = cols
        self.mine_count = mine_count
        self.grid: list[list[Cell]] = []
        self._generate()

    def _generate(self):
        self.grid = [[Cell(row=r, col=c) for c in range(self.cols)] for r in range(self.rows)]
        # Place mines
        positions = random.sample(range(self.rows * self.cols), self.mine_count)
        for pos in positions:
            r, c = pos // self.cols, pos % self.cols
            self.grid[r][c].is_mine = True
        # Calculate adjacency
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c].is_mine:
                    self.grid[r][c].adjacent_mines = self._count_adjacent(r, c)

    def _count_adjacent(self, r, c):
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.grid[nr][nc].is_mine:
                        count += 1
        return count

    def reveal(self, r, c) -> bool:
        cell = self.grid[r][c]
        if cell.is_flagged or cell.is_revealed:
            return True
        if cell.is_mine:
            cell.is_revealed = True
            return False
        # Flood fill for zeros
        cell.is_revealed = True
        if cell.adjacent_mines == 0:
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
        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbors.append(self.grid[nr][nc])
        return neighbors

    def is_won(self) -> bool:
        for row in self.grid:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return False
        return True

    def render(self, highlight: Optional[tuple] = None):
        # Column headers
        print(f"   {'  '.join(f'{c:2d}' for c in range(self.cols))}")
        print(f"   {'--' * self.cols}")
        for r in range(self.rows):
            cells = []
            for c in range(self.cols):
                cell = self.grid[r][c]
                hl = highlight and highlight == (r, c)
                if cell.is_flagged:
                    cells.append(f"{YELLOW}⚑{R}" if not hl else f"{BOLD}{YELLOW}[⚑]{R}")
                elif not cell.is_revealed:
                    cells.append(f"{GREY}■{R}" if not hl else f"{BOLD}{CYAN}[■]{R}")
                elif cell.is_mine:
                    cells.append(f"{RED}💣{R}")
                elif cell.adjacent_mines == 0:
                    cells.append(f"  ")
                else:
                    color = [GREY, BLUE, GREEN, YELLOW, RED, RED, CYAN, CYAN, GREY][cell.adjacent_mines]
                    cells.append(f"{color}{cell.adjacent_mines}{R} ")
            print(f"{r:2d}│ {''.join(cells)}")
        print()


class MinesweeperSolver:
    """CSP + Probability solver for autonomous Minesweeper play."""

    def __init__(self, board: MinesweeperBoard):
        self.board = board
        self.move_count = 0
        self.won = False
        self.lost = False

    def solve(self):
        # First move: reveal center cell (safest start)
        center_r, center_c = self.board.rows // 2, self.board.cols // 2
        self._make_move(center_r, center_c, "initial safe cell")

        # Main loop: apply constraint propagation, then probability fallback
        while not self.board.is_won() and not self.lost:
            moved = self._constraint_propagation()
            if not moved:
                moved = self._probability_move()
            if not moved:
                break  # No moves available

        self.won = self.board.is_won()
        self._print_result()

    def _constraint_propagation(self) -> bool:
        """
        Apply CSP rules:
        Rule 1: If a revealed cell's number == flagged neighbors, all unrevealed neighbors are safe.
        Rule 2: If a revealed cell's number - flagged == unrevealed neighbors count, all unrevealed are mines.
        """
        made_move = False
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.grid[r][c]
                if not cell.is_revealed or cell.adjacent_mines == 0:
                    continue

                neighbors = self.board.get_neighbors(r, c)
                flagged = sum(1 for n in neighbors if n.is_flagged)
                unrevealed = [n for n in neighbors if not n.is_revealed and not n.is_flagged]

                if not unrevealed:
                    continue

                # Rule 1: All mines found → remaining are safe
                if cell.adjacent_mines == flagged:
                    for n in unrevealed:
                        safe_r, safe_c = n.row, n.col
                        self._make_move(safe_r, safe_c, f"CSP safe (from {r},{c})")
                        made_move = True
                        if self.lost:
                            return made_move

                # Rule 2: Remaining unrevealed must be mines
                elif cell.adjacent_mines - flagged == len(unrevealed):
                    for n in unrevealed:
                        self.board.flag(n.row, n.col)
                        print(f"  {YELLOW}⚑ Flagged ({n.row},{n.col}) — CSP mine inference from ({r},{c}){R}")
                        made_move = True

        return made_move

    def _probability_move(self) -> bool:
        """When no deterministic move exists, pick the unrevealed cell with lowest mine probability."""
        # Build probability estimate for each unrevealed cell
        probs: dict[tuple, float] = {}
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                cell = self.board.grid[r][c]
                if cell.is_revealed or cell.is_flagged:
                    continue

                # Check if any revealed neighbor constrains this cell
                neighbors = self.board.get_neighbors(r, c)
                max_prob = self._estimate_prob(r, c, neighbors)
                probs[(r, c)] = max_prob

        if not probs:
            return False

        # Pick lowest probability cell
        best = min(probs, key=probs.get)
        prob = probs[best]
        label = f"prob={prob:.2%}" if prob < 1.0 else "forced"
        self._make_move(best[0], best[1], f"probability move ({label})")
        return True

    def _estimate_prob(self, r, c, neighbors) -> float:
        """Estimate probability that cell (r,c) is a mine based on neighbor constraints."""
        constraints = []
        for n in neighbors:
            if n.is_revealed and n.adjacent_mines > 0:
                flagged = sum(1 for nn in self.board.get_neighbors(n.row, n.col) if nn.is_flagged)
                unrevealed = [nn for nn in self.board.get_neighbors(n.row, n.col) if not nn.is_revealed and not nn.is_flagged]
                if unrevealed:
                    remaining_mines = n.adjacent_mines - flagged
                    prob = remaining_mines / len(unrevealed)
                    constraints.append(prob)

        if constraints:
            return max(constraints)  # Worst-case probability

        # No constraints: use global mine density
        total_mines = self.board.mine_count
        unrevealed_count = sum(1 for row in self.board.grid for cell in row if not cell.is_revealed and not cell.is_flagged)
        return total_mines / max(unrevealed_count, 1)

    def _make_move(self, r, c, reason: str):
        self.move_count += 1
        print(f"\n{BOLD}Move #{self.move_count}{R}: Reveal ({r},{c}) — {CYAN}{reason}{R}")
        success = self.board.reveal(r, c)
        self.board.render(highlight=(r, c))
        if not success:
            self.lost = True
            print(f"{RED}💥 HIT A MINE at ({r},{c}) — Game Over{R}")

    def _print_result(self):
        print(f"\n{'='*50}")
        if self.won:
            print(f"{GREEN}{BOLD}✅ SOLVED in {self.move_count} moves — CSP + probability engine{R}")
        else:
            print(f"{RED}{BOLD}💥 FAILED after {self.move_count} moves — hit a mine{R}")
        print(f"{'='*50}")


if __name__ == "__main__":
    print(f"\n{BOLD}{'='*50}{R}")
    print(f"{BOLD}Minesweeper CSP Solver — 0-Player Autonomous{R}")
    print(f"{BOLD}{'='*50}{R}\n")

    random.seed(42)  # Reproducible for demo
    board = MinesweeperBoard(rows=10, cols=10, mine_count=12)
    solver = MinesweeperSolver(board)
    solver.solve()
