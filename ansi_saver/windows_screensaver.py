from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from .viewer import load_paths, read_ansi_text

DEFAULT_DELAY_SECONDS = 8.0
DEFAULT_FOLDER = str(Path.home())


def _appdata_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "AnsiSaver"
    return Path.home() / ".config" / "AnsiSaver"


def settings_path() -> Path:
    return _appdata_dir() / "windows_screensaver.json"


def load_settings() -> dict[str, Any]:
    path = settings_path()
    if not path.exists():
        return {"folder": DEFAULT_FOLDER, "delay": DEFAULT_DELAY_SECONDS}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"folder": DEFAULT_FOLDER, "delay": DEFAULT_DELAY_SECONDS}
    folder = str(data.get("folder") or DEFAULT_FOLDER)
    delay = float(data.get("delay") or DEFAULT_DELAY_SECONDS)
    return {"folder": folder, "delay": max(delay, 0)}


def save_settings(folder: str, delay: float) -> None:
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"folder": folder, "delay": max(float(delay), 0)}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_windows_scr_args(argv: list[str]) -> tuple[str, str | None]:
    if not argv:
        return ("config", None)

    token = argv[0].strip().lower()
    if token.startswith("/s"):
        return ("start", None)
    if token.startswith("/c"):
        # /c or /c:12345 style
        handle = None
        if ":" in argv[0]:
            handle = argv[0].split(":", 1)[1]
        elif len(argv) > 1:
            handle = argv[1]
        return ("config", handle)
    if token.startswith("/p"):
        handle = None
        if ":" in argv[0]:
            handle = argv[0].split(":", 1)[1]
        elif len(argv) > 1:
            handle = argv[1]
        return ("preview", handle)
    return ("config", None)


def run_config_dialog() -> int:
    import tkinter as tk
    from tkinter import filedialog, messagebox

    settings = load_settings()

    root = tk.Tk()
    root.title("AnsiSaver Windows Configuration")
    root.resizable(False, False)

    tk.Label(root, text="ANSI Folder:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
    folder_var = tk.StringVar(value=settings["folder"])
    folder_entry = tk.Entry(root, width=54, textvariable=folder_var)
    folder_entry.grid(row=0, column=1, padx=8, pady=8)

    def browse() -> None:
        selected = filedialog.askdirectory(initialdir=folder_var.get() or str(Path.home()))
        if selected:
            folder_var.set(selected)

    tk.Button(root, text="Browse...", command=browse).grid(row=0, column=2, padx=8, pady=8)

    tk.Label(root, text="Delay (seconds):").grid(row=1, column=0, padx=8, pady=8, sticky="w")
    delay_var = tk.StringVar(value=str(settings["delay"]))
    tk.Entry(root, width=12, textvariable=delay_var).grid(row=1, column=1, padx=8, pady=8, sticky="w")

    def save_and_close() -> None:
        folder = folder_var.get().strip()
        try:
            delay = float(delay_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid value", "Delay must be a number.")
            return
        if not folder:
            messagebox.showerror("Invalid value", "Folder must not be empty.")
            return
        save_settings(folder, delay)
        root.destroy()

    tk.Button(root, text="Save", command=save_and_close).grid(row=2, column=1, padx=8, pady=12, sticky="e")
    tk.Button(root, text="Cancel", command=root.destroy).grid(row=2, column=2, padx=8, pady=12, sticky="w")

    root.mainloop()
    return 0


def run_fullscreen_screensaver(folder: str, delay_seconds: float) -> int:
    import tkinter as tk

    paths = load_paths(folder=folder, pack_url=None)
    if not paths:
        return 1

    root = tk.Tk()
    root.configure(bg="black")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.config(cursor="none")

    text = tk.Text(
        root,
        bg="black",
        fg="#d0d0d0",
        insertbackground="#d0d0d0",
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        font=("Consolas", 12),
        wrap="none",
    )
    text.pack(fill="both", expand=True)

    for event_name in ["<Motion>", "<Key>", "<Button>", "<MouseWheel>", "<Escape>"]:
        root.bind(event_name, lambda _e: root.destroy())

    delay_ms = max(int(delay_seconds * 1000), 0)
    index = {"value": 0}

    def show_next() -> None:
        path = paths[index["value"] % len(paths)]
        content = read_ansi_text(path)
        text.delete("1.0", "end")
        text.insert("1.0", f"{Path(path).name}\n\n")
        text.insert("end", content)
        index["value"] += 1
        root.after(delay_ms or 1, show_next)

    show_next()
    root.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    # If launched as .scr, Windows passes /s, /c, /p variants.
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0].startswith("/"):
        action, _ = parse_windows_scr_args(args)
        if action == "start":
            settings = load_settings()
            return run_fullscreen_screensaver(
                folder=settings["folder"],
                delay_seconds=float(settings["delay"]),
            )
        if action == "preview":
            return 0
        return run_config_dialog()

    parser = argparse.ArgumentParser(prog="ansi-saver-scr", description="AnsiSaver Windows screensaver host")
    sub = parser.add_subparsers(dest="command", required=True)

    config = sub.add_parser("config", help="Open configuration dialog")
    config.add_argument("--folder", help="Optional folder override to save immediately")
    config.add_argument("--delay", type=float, help="Optional delay override to save immediately")

    start = sub.add_parser("start", help="Launch fullscreen screensaver")
    start.add_argument("--folder", help="Folder containing ANSI files")
    start.add_argument("--delay", type=float, default=None, help="Delay in seconds between files")

    ns = parser.parse_args(args)

    if ns.command == "config":
        if ns.folder or ns.delay is not None:
            current = load_settings()
            save_settings(ns.folder or current["folder"], ns.delay if ns.delay is not None else current["delay"])
            return 0
        return run_config_dialog()

    if ns.command == "start":
        current = load_settings()
        folder = ns.folder or current["folder"]
        delay = ns.delay if ns.delay is not None else current["delay"]
        return run_fullscreen_screensaver(folder=folder, delay_seconds=float(delay))

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
