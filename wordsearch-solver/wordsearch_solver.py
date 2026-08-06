#!/usr/bin/env python3
"""
Word Search Solver — Matrix Manipulation & String Search Algorithms

Autonomous 0-player solver that:
1. Generates a word search grid with words placed in 8 directions
2. Scans the grid using brute-force AND optimized (KMP) string matching
3. Highlights found words in the solved grid
4. Benchmarks brute-force vs KMP scan performance

Directions: N, NE, E, SE, S, SW, W, NW

Run: python3 wordsearch_solver.py
"""

import random
import time
from dataclasses import dataclass, field
from typing import Optional

# ANSI colors
R = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
GREY = "\033[90m"
MAGENTA = "\033[95m"

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIRECTIONS = [
    (-1, 0),   # N
    (-1, 1),   # NE
    (0, 1),    # E
    (1, 1),    # SE
    (1, 0),    # S
    (1, -1),   # SW
    (0, -1),   # W
    (-1, -1),  # NW
]
DIR_NAMES = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


@dataclass
class FoundWord:
    word: str
    start_row: int
    start_col: int
    direction: int
    cells: list = field(default_factory=list)


class WordSearchGrid:
    def __init__(self, size=15, words=None):
        self.size = size
        self.grid = [[' ' for _ in range(size)] for _ in range(size)]
        self.placed_words: list[tuple[str, int, int, int]] = []  # (word, row, col, dir_idx)
        self.found: list[FoundWord] = []

        if words is None:
            words = ["PYTHON", "ALGORITHM", "MATRIX", "SEARCH", "STRING",
                     "GRID", "SCAN", "PATTERN", "MATCH", "SOLVE"]

        self.words = words
        self._generate()

    def _generate(self):
        for word in self.words:
            placed = False
            attempts = 0
            while not placed and attempts < 200:
                attempts += 1
                dir_idx = random.randint(0, 7)
                dr, dc = DIRECTIONS[dir_idx]
                max_r = self.size - 1
                max_c = self.size - 1

                # Calculate valid start range
                word_len = len(word)
                if dr > 0:
                    r_range = max_r - word_len + 1
                elif dr < 0:
                    r_range = max_r - word_len + 1
                    r_start = word_len - 1
                else:
                    r_start = 0
                    r_range = max_r

                if dc > 0:
                    c_range = max_c - word_len + 1
                elif dc < 0:
                    c_start = word_len - 1
                    c_range = max_c
                else:
                    c_start = 0
                    c_range = max_c

                # Simpler: pick random start and check
                r = random.randint(0, max_r)
                c = random.randint(0, max_c)

                # Check if word fits
                fits = True
                cells = []
                for i, ch in enumerate(word):
                    nr = r + dr * i
                    nc = c + dc * i
                    if nr < 0 or nr >= self.size or nc < 0 or nc >= self.size:
                        fits = False
                        break
                    if self.grid[nr][nc] != ' ' and self.grid[nr][nc] != ch:
                        fits = False
                        break
                    cells.append((nr, nc))

                if fits:
                    for i, ch in enumerate(word):
                        self.grid[cells[i][0]][cells[i][1]] = ch
                    self.placed_words.append((word, r, c, dir_idx))
                    placed = True

        # Fill empty cells with random letters
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == ' ':
                    self.grid[r][c] = random.choice(ALPHABET)

    def brute_force_scan(self, words: list[str]) -> list[FoundWord]:
        """Brute-force: check every cell, every direction, character by character."""
        found = []
        for word in words:
            wlen = len(word)
            for r in range(self.size):
                for c in range(self.size):
                    for d_idx, (dr, dc) in enumerate(DIRECTIONS):
                        match = True
                        cells = []
                        for i in range(wlen):
                            nr = r + dr * i
                            nc = c + dc * i
                            if nr < 0 or nr >= self.size or nc < 0 or nc >= self.size:
                                match = False
                                break
                            if self.grid[nr][nc] != word[i]:
                                match = False
                                break
                            cells.append((nr, nc))
                        if match:
                            found.append(FoundWord(word, r, c, d_idx, cells))
        return found

    def kmp_scan(self, words: list[str]) -> list[FoundWord]:
        """Optimized scan using KMP failure function for each direction line."""
        found = []
        # Extract all lines in all 8 directions, then KMP match each word
        lines = self._extract_all_lines()
        for word in words:
            for line_info in lines:
                matches = self._kmp_search(word, line_info['text'])
                for match_start in matches:
                    start_r = line_info['cells'][match_start][0]
                    start_c = line_info['cells'][match_start][1]
                    cells = line_info['cells'][match_start:match_start + len(word)]
                    found.append(FoundWord(word, start_r, start_c, line_info['dir'], cells))
        return found

    def _extract_all_lines(self) -> list[dict]:
        """Extract all possible lines (strings) in all 8 directions for KMP scanning."""
        lines = []
        for d_idx, (dr, dc) in enumerate(DIRECTIONS):
            # Find all starting points that produce non-trivial lines
            for r in range(self.size):
                for c in range(self.size):
                    text = []
                    cells = []
                    nr, nc = r, c
                    while 0 <= nr < self.size and 0 <= nc < self.size:
                        text.append(self.grid[nr][nc])
                        cells.append((nr, nc))
                        nr += dr
                        nc += dc
                    if len(text) >= 2:
                        lines.append({'text': ''.join(text), 'cells': cells, 'dir': d_idx})
        return lines

    @staticmethod
    def _kmp_search(pattern: str, text: str) -> list[int]:
        """KMP (Knuth-Morris-Pratt) string matching. Returns list of match start indices."""
        if not pattern:
            return []
        # Build failure function
        failure = [0] * len(pattern)
        j = 0
        for i in range(1, len(pattern)):
            while j > 0 and pattern[i] != pattern[j]:
                j = failure[j - 1]
            if pattern[i] == pattern[j]:
                j += 1
            failure[i] = j

        # Search
        matches = []
        j = 0
        for i in range(len(text)):
            while j > 0 and text[i] != pattern[j]:
                j = failure[j - 1]
            if text[i] == pattern[j]:
                j += 1
            if j == len(pattern):
                matches.append(i - len(pattern) + 1)
                j = failure[j - 1]
        return matches

    def render_solved(self, found_words: list[FoundWord]):
        """Render grid with found words highlighted."""
        # Build highlight map
        highlight = {}
        for i, fw in enumerate(found_words):
            color = [GREEN, CYAN, YELLOW, RED, MAGENTA][i % 5]
            for r, c in fw.cells:
                highlight[(r, c)] = color

        print(f"\n{BOLD}=== SOLVED GRID ==={R}\n")
        print("   " + " ".join(f"{i%10}" for i in range(self.size)))
        print(f"  {'─' * (self.size * 2 + 1)}")
        for r in range(self.size):
            row_str = []
            for c in range(self.size):
                ch = self.grid[r][c]
                if (r, c) in highlight:
                    color = highlight[(r, c)]
                    row_str.append(f"{BOLD}{color}{ch}{R}")
                else:
                    row_str.append(f"{GREY}{ch}{R}")
            print(f"{r%10:2d}│{''.join(row_str)}")

        print(f"\n{BOLD}Found {len(found_words)} words:{R}")
        for fw in found_words:
            cells_str = " → ".join(f"({r},{c})" for r, c in fw.cells[:3])
            print(f"  {GREEN}✓{R} {fw.word:<12} at {DIR_NAMES[fw.direction]:>2s} — {cells_str}...")


def benchmark(grid: WordSearchGrid, words: list[str]):
    """Compare brute-force vs KMP scan performance."""
    print(f"\n{BOLD}{'='*50}{R}")
    print(f"{BOLD}Performance Benchmark: Brute-Force vs KMP{R}")
    print(f"{BOLD}{'='*50}{R}")
    print(f"Grid size: {grid.size}x{grid.size}")
    print(f"Words to find: {len(words)}")

    # Brute-force
    start = time.perf_counter_ns()
    bf_found = grid.brute_force_scan(words)
    bf_time = time.perf_counter_ns() - start
    print(f"\n{YELLOW}Brute-Force:{R}")
    print(f"  Found: {len(bf_found)} words")
    print(f"  Time:  {bf_time / 1000:.1f} µs ({bf_time} ns)")

    # KMP
    start = time.perf_counter_ns()
    kmp_found = grid.kmp_scan(words)
    kmp_time = time.perf_counter_ns() - start
    print(f"\n{CYAN}KMP (Knuth-Morris-Pratt):{R}")
    print(f"  Found: {len(kmp_found)} words")
    print(f"  Time:  {kmp_time / 1000:.1f} µs ({kmp_time} ns)")

    speedup = bf_time / kmp_time if kmp_time > 0 else float('inf')
    print(f"\n{GREEN}KMP speedup: {speedup:.2f}x{R}")
    print(f"{'='*50}\n")

    return bf_found, kmp_found


if __name__ == "__main__":
    print(f"\n{BOLD}{'='*50}{R}")
    print(f"{BOLD}Word Search Solver — Matrix & String Search{R}")
    print(f"{BOLD}{'='*50}{R}")
    print(f"  Grid generation: 8-directional word placement")
    print(f"  Brute-force scan: O(n*m*8*w)")
    print(f"  KMP scan: O(n+m) per line per word")

    random.seed(42)
    words = ["PYTHON", "ALGORITHM", "MATRIX", "SEARCH", "STRING",
             "GRID", "SCAN", "PATTERN", "MATCH", "SOLVE"]

    grid = WordSearchGrid(size=15, words=words)

    print(f"\n{BOLD}=== GENERATED GRID ==={R}\n")
    for r in range(grid.size):
        print("  " + " ".join(grid.grid[r][c] for c in range(grid.size)))

    print(f"\nPlaced words: {', '.join(w for w, *_ in grid.placed_words)}")

    # Benchmark
    bf_found, kmp_found = benchmark(grid, words)

    # Render solved grid using KMP results
    grid.render_solved(kmp_found)
