#!/usr/bin/env python3
"""
Word Search Solver — Matrix Manipulation & KMP String Matching with GUI

Autonomous 0-player solver with tkinter GUI:
  - 8-directional word placement
  - Brute-force vs KMP string matching benchmark
  - Visual grid with found words highlighted in colors

Clone and run: python3 wordsearch_solver.py
"""

import random
import time
import tkinter as tk
from dataclasses import dataclass, field
from typing import Optional

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIRECTIONS = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
DIR_NAMES = ["N","NE","E","SE","S","SW","W","NW"]
WORD_COLORS = ["#44ff44", "#44ffff", "#ffff44", "#ff4444", "#ff44ff",
               "#44aaff", "#ff8844", "#aa44ff", "#44ffaa", "#ffaaaa"]

BG = "#0d0d1a"
GREY_CELL = "#2a2a3a"
TEXT_LIGHT = "#e0e0e0"


@dataclass
class FoundWord:
    word: str
    start_r: int
    start_c: int
    direction: int
    cells: list = field(default_factory=list)


class WordSearchGrid:
    def __init__(self, size=14, words=None):
        self.size = size
        self.grid = [[' ' for _ in range(size)] for _ in range(size)]
        self.placed = []
        self.words = words or ["PYTHON","ALGORITHM","MATRIX","SEARCH","STRING",
                               "GRID","SCAN","PATTERN","MATCH","SOLVE"]
        self._generate()

    def _generate(self):
        for word in self.words:
            for attempt in range(200):
                d_idx = random.randint(0, 7)
                dr, dc = DIRECTIONS[d_idx]
                r = random.randint(0, self.size - 1)
                c = random.randint(0, self.size - 1)
                cells = []
                fits = True
                for i, ch in enumerate(word):
                    nr, nc = r + dr*i, c + dc*i
                    if nr < 0 or nr >= self.size or nc < 0 or nc >= self.size:
                        fits = False; break
                    if self.grid[nr][nc] not in (' ', ch):
                        fits = False; break
                    cells.append((nr, nc))
                if fits:
                    for i, ch in enumerate(word):
                        self.grid[cells[i][0]][cells[i][1]] = ch
                    self.placed.append((word, r, c, d_idx))
                    break
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == ' ':
                    self.grid[r][c] = random.choice(ALPHABET)

    def brute_force(self, words):
        found = []
        for word in words:
            for r in range(self.size):
                for c in range(self.size):
                    for d_idx, (dr, dc) in enumerate(DIRECTIONS):
                        ok = True
                        cells = []
                        for i in range(len(word)):
                            nr, nc = r+dr*i, c+dc*i
                            if nr < 0 or nr >= self.size or nc < 0 or nc >= self.size:
                                ok = False; break
                            if self.grid[nr][nc] != word[i]:
                                ok = False; break
                            cells.append((nr, nc))
                        if ok:
                            found.append(FoundWord(word, r, c, d_idx, cells))
        return found

    def kmp_scan(self, words):
        lines = self._extract_lines()
        found = []
        for word in words:
            for line in lines:
                matches = self._kmp(word, line['text'])
                for ms in matches:
                    cells = line['cells'][ms:ms+len(word)]
                    found.append(FoundWord(word, cells[0][0], cells[0][1], line['dir'], cells))
        return found

    def _extract_lines(self):
        lines = []
        for d_idx, (dr, dc) in enumerate(DIRECTIONS):
            for r in range(self.size):
                for c in range(self.size):
                    text, cells = [], []
                    nr, nc = r, c
                    while 0 <= nr < self.size and 0 <= nc < self.size:
                        text.append(self.grid[nr][nc])
                        cells.append((nr, nc))
                        nr += dr; nc += dc
                    if len(text) >= 2:
                        lines.append({'text': ''.join(text), 'cells': cells, 'dir': d_idx})
        return lines

    @staticmethod
    def _kmp(pattern, text):
        if not pattern:
            return []
        fail = [0] * len(pattern)
        j = 0
        for i in range(1, len(pattern)):
            while j > 0 and pattern[i] != pattern[j]:
                j = fail[j-1]
            if pattern[i] == pattern[j]:
                j += 1
            fail[i] = j
        matches = []
        j = 0
        for i in range(len(text)):
            while j > 0 and text[i] != pattern[j]:
                j = fail[j-1]
            if text[i] == pattern[j]:
                j += 1
            if j == len(pattern):
                matches.append(i - len(pattern) + 1)
                j = fail[j-1]
        return matches


class WordSearchGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Word Search Solver — KMP String Matching")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        tk.Label(self.root, text="Word Search Solver", font=("Helvetica", 16, "bold"),
                 fg="#ffffff", bg=BG).pack(pady=5)
        tk.Label(self.root, text="Matrix Manipulation · 8-Directional Scanning · KMP",
                 font=("Helvetica", 10), fg=TEXT_LIGHT, bg=BG).pack()

        # Info
        self.info = tk.Frame(self.root, bg=BG)
        self.info.pack(pady=5, padx=10, fill="x")
        self.time_label = tk.Label(self.info, text="", font=("Courier", 10), fg=TEXT_LIGHT, bg=BG)
        self.time_label.pack(side="left", padx=5)
        self.found_label = tk.Label(self.info, text="Found: 0", font=("Courier", 10), fg=TEXT_LIGHT, bg=BG)
        self.found_label.pack(side="right", padx=5)

        # Grid
        random.seed(42)
        self.grid_data = WordSearchGrid(14)
        self.cell_size = 28

        w = self.grid_data.size * self.cell_size
        self.canvas = tk.Canvas(self.root, width=w, height=w, bg=BG, highlightthickness=0)
        self.canvas.pack(padx=10, pady=5)

        # Word list
        self.word_frame = tk.Frame(self.root, bg=BG)
        self.word_frame.pack(pady=5, padx=10)
        self.word_labels = {}
        for word in self.grid_data.words:
            lbl = tk.Label(self.word_frame, text=word, font=("Courier", 10, "bold"),
                         fg="#888888", bg=BG, padx=8)
            lbl.pack(side="left", padx=2)
            self.word_labels[word] = lbl

        # Footer
        tk.Label(self.root, text="Solving automatically... · R: new puzzle",
                 font=("Helvetica", 9), fg="#444444", bg=BG).pack(pady=3)

        self.root.bind("r", lambda e: self.reset())

        self.found_words = []
        self.draw_grid()
        self.root.after(500, self.solve_step)

    def draw_grid(self, highlight=None):
        self.canvas.delete("all")
        highlight_map = {}
        for i, fw in enumerate(self.found_words):
            color = WORD_COLORS[i % len(WORD_COLORS)]
            for r, c in fw.cells:
                highlight_map[(r, c)] = color

        for r in range(self.grid_data.size):
            for c in range(self.grid_data.size):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                if (r, c) in highlight_map:
                    bg = highlight_map[(r, c)]
                    fg = "#000000"
                else:
                    bg = GREY_CELL
                    fg = TEXT_LIGHT
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="#1a1a2a", width=1)
                self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                       text=self.grid_data.grid[r][c],
                                       font=("Courier", 13, "bold"), fill=fg)
        self.root.update()

    def solve_step(self):
        if not self.found_words:
            # Benchmark
            t0 = time.perf_counter_ns()
            bf = self.grid_data.brute_force(self.grid_data.words)
            bf_time = time.perf_counter_ns() - t0

            t0 = time.perf_counter_ns()
            kmp = self.grid_data.kmp_scan(self.grid_data.words)
            kmp_time = time.perf_counter_ns() - t0

            speedup = bf_time / kmp_time if kmp_time > 0 else 0
            self.time_label.config(
                text=f"BF: {bf_time//1000}µs | KMP: {kmp_time//1000}µs | {speedup:.2f}x speedup",
                fg="#44ff44"
            )
            # Use KMP results, deduplicate by word
            seen = set()
            unique = []
            for fw in kmp:
                if fw.word not in seen:
                    seen.add(fw.word)
                    unique.append(fw)
            self._to_reveal = unique
            self._reveal_idx = 0

        if self._reveal_idx < len(self._to_reveal):
            fw = self._to_reveal[self._reveal_idx]
            self.found_words.append(fw)
            self._reveal_idx += 1
            color = WORD_COLORS[(len(self.found_words)-1) % len(WORD_COLORS)]
            lbl = self.word_labels.get(fw.word)
            if lbl:
                lbl.config(fg=color)
            self.found_label.config(text=f"Found: {len(self.found_words)}")
            self.draw_grid()
            self.root.after(400, self.solve_step)
        else:
            self.time_label.config(text=f"✅ Solved! {len(self.found_words)} words found · KMP speedup shown above", fg="#44ff44")

    def reset(self):
        self.grid_data = WordSearchGrid(14)
        self.found_words = []
        for word, lbl in self.word_labels.items():
            lbl.config(fg="#888888")
        self.found_label.config(text="Found: 0")
        self.time_label.config(text="")
        self.draw_grid()
        self.root.after(500, self.solve_step)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    random.seed(42)
    app = WordSearchGUI()
    app.run()
