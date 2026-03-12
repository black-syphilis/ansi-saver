from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cell:
    char: str = " "
    fg: str = "#d0d0d0"
    bg: str = "#000000"


_COLOR_LOW = {
    0: "#000000",
    1: "#aa0000",
    2: "#00aa00",
    3: "#aa5500",
    4: "#0000aa",
    5: "#aa00aa",
    6: "#00aaaa",
    7: "#aaaaaa",
}

_COLOR_HIGH = {
    0: "#555555",
    1: "#ff5555",
    2: "#55ff55",
    3: "#ffff55",
    4: "#5555ff",
    5: "#ff55ff",
    6: "#55ffff",
    7: "#ffffff",
}


def _empty_grid(columns: int, rows: int) -> list[list[Cell]]:
    return [[Cell() for _ in range(columns)] for _ in range(rows)]


def parse_ansi(
    text: str,
    *,
    columns: int = 80,
    rows: int = 100,
) -> list[list[Cell]]:
    grid = _empty_grid(columns, rows)
    row = 0
    col = 0
    bright = False
    fg = "#d0d0d0"
    bg = "#000000"

    def clamp_cursor() -> None:
        nonlocal row, col
        row = max(0, min(rows - 1, row))
        col = max(0, min(columns - 1, col))

    i = 0
    n = len(text)
    while i < n:
        ch = text[i]

        if ch == "\x1b" and i + 1 < n and text[i + 1] == "[":
            j = i + 2
            while j < n and not ("@" <= text[j] <= "~"):
                j += 1
            if j >= n:
                break
            cmd = text[j]
            raw = text[i + 2 : j]
            params = [p for p in raw.split(";") if p != ""]
            vals = [int(p) if p.isdigit() else 0 for p in params] if params else [0]

            if cmd == "m":
                for v in vals:
                    if v == 0:
                        bright = False
                        fg = "#d0d0d0"
                        bg = "#000000"
                    elif v == 1:
                        bright = True
                    elif v == 22:
                        bright = False
                    elif 30 <= v <= 37:
                        fg = (_COLOR_HIGH if bright else _COLOR_LOW)[v - 30]
                    elif 90 <= v <= 97:
                        fg = _COLOR_HIGH[v - 90]
                    elif 40 <= v <= 47:
                        bg = _COLOR_LOW[v - 40]
                    elif 100 <= v <= 107:
                        bg = _COLOR_HIGH[v - 100]
                    elif v == 39:
                        fg = "#d0d0d0"
                    elif v == 49:
                        bg = "#000000"
            elif cmd == "A":
                row -= vals[0] if vals else 1
                clamp_cursor()
            elif cmd == "B":
                row += vals[0] if vals else 1
                clamp_cursor()
            elif cmd == "C":
                col += vals[0] if vals else 1
                clamp_cursor()
            elif cmd == "D":
                col -= vals[0] if vals else 1
                clamp_cursor()
            elif cmd in {"H", "f"}:
                r = (vals[0] - 1) if len(vals) >= 1 else 0
                c = (vals[1] - 1) if len(vals) >= 2 else 0
                row, col = r, c
                clamp_cursor()
            elif cmd == "J":
                mode = vals[0] if vals else 0
                if mode == 2:
                    grid = _empty_grid(columns, rows)
                    row, col = 0, 0
            elif cmd == "K":
                mode = vals[0] if vals else 0
                if mode == 0:
                    for c in range(col, columns):
                        grid[row][c] = Cell(" ", fg, bg)
                elif mode == 1:
                    for c in range(0, col + 1):
                        grid[row][c] = Cell(" ", fg, bg)
                elif mode == 2:
                    for c in range(columns):
                        grid[row][c] = Cell(" ", fg, bg)

            i = j + 1
            continue

        if ch == "\r":
            col = 0
            i += 1
            continue
        if ch == "\n":
            row += 1
            if row >= rows:
                row = rows - 1
            i += 1
            continue
        if ch == "\b":
            col = max(0, col - 1)
            i += 1
            continue
        if ch == "\t":
            col = min(columns - 1, ((col // 8) + 1) * 8)
            i += 1
            continue

        if ord(ch) >= 32:
            if 0 <= row < rows and 0 <= col < columns:
                grid[row][col] = Cell(ch, fg, bg)
            col += 1
            if col >= columns:
                col = 0
                row += 1
                if row >= rows:
                    row = rows - 1
        i += 1

    return grid
