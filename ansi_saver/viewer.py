from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from .art_source import FolderSource, PackSource


def clear_screen() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def read_ansi_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="latin-1", errors="ignore")


def load_paths(folder: str | None, pack_url: str | None) -> list[str]:
    if folder:
        return sorted(FolderSource(folder).load_art_paths())
    if pack_url:
        return sorted(PackSource(pack_url).load_art_paths())
    return []


def run_viewer(
    *,
    folder: str | None = None,
    pack_url: str | None = None,
    delay_seconds: float = 6.0,
    once: bool = False,
    clear_between: bool = True,
) -> int:
    paths = load_paths(folder=folder, pack_url=pack_url)
    if not paths:
        print("No ANSI files found to display.", file=sys.stderr)
        return 1

    print("Viewer started. Press Ctrl+C to stop.")
    if delay_seconds < 0:
        delay_seconds = 0

    try:
        while True:
            for path in paths:
                if clear_between:
                    clear_screen()
                print(f"--- {Path(path).name} ---\n")
                print(read_ansi_text(path), end="")
                sys.stdout.flush()
                if delay_seconds:
                    time.sleep(delay_seconds)
            if once:
                break
    except KeyboardInterrupt:
        return 0

    return 0
