from __future__ import annotations

import argparse

from .art_source import FolderSource
from .pack_fetcher import PackFetcher


def main() -> int:
    parser = argparse.ArgumentParser(prog="ansi-saver", description="AnsiSaver Python CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch-pack", help="List ANSI-like files from a 16colo pack URL")
    fetch.add_argument("url")

    scan = sub.add_parser("scan-folder", help="List ANSI-like files from a local folder")
    scan.add_argument("path")

    args = parser.parse_args()

    if args.command == "fetch-pack":
        for filename in PackFetcher.fetch_file_list(args.url):
            print(filename)
        return 0

    if args.command == "scan-folder":
        for path in FolderSource(args.path).load_art_paths():
            print(path)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
