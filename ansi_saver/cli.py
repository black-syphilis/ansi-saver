from __future__ import annotations

import argparse

from .art_source import FolderSource
from .pack_fetcher import PackFetcher
from .viewer import run_viewer


def main() -> int:
    parser = argparse.ArgumentParser(prog="ansi-saver", description="AnsiSaver Python CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch-pack", help="List ANSI-like files from a 16colo pack URL")
    fetch.add_argument("url")

    scan = sub.add_parser("scan-folder", help="List ANSI-like files from a local folder")
    scan.add_argument("path")

    viewer = sub.add_parser("viewer", help="Show ANSI files in a terminal slideshow")
    source = viewer.add_mutually_exclusive_group(required=True)
    source.add_argument("--folder", help="Local folder containing ANSI files")
    source.add_argument("--pack-url", help="16colo pack URL to fetch and display")
    viewer.add_argument("--delay", type=float, default=6.0, help="Delay in seconds between files")
    viewer.add_argument("--once", action="store_true", help="Display each file once and exit")
    viewer.add_argument("--no-clear", action="store_true", help="Do not clear terminal between files")

    args = parser.parse_args()

    if args.command == "fetch-pack":
        for filename in PackFetcher.fetch_file_list(args.url):
            print(filename)
        return 0

    if args.command == "scan-folder":
        for path in FolderSource(args.path).load_art_paths():
            print(path)
        return 0

    if args.command == "viewer":
        return run_viewer(
            folder=args.folder,
            pack_url=args.pack_url,
            delay_seconds=args.delay,
            once=args.once,
            clear_between=not args.no_clear,
        )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
