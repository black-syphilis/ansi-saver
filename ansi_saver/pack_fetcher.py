from __future__ import annotations

import re
from urllib.parse import quote
from urllib.request import Request, urlopen

from .cache import Cache


class PackFetcher:
    _ANS_PATTERN = re.compile(
        r'href="[^"]*?/([^/"]+\.(?:ans|ANS|ice|ICE|asc|ASC|bin|BIN|xb|XB|pcb|PCB|adf|ADF))"'
    )

    @staticmethod
    def fetch_file_list(pack_url: str, timeout: int = 20) -> list[str]:
        normalized = pack_url if pack_url.endswith("/") else f"{pack_url}/"
        try:
            req = Request(normalized, headers={"User-Agent": "ansi-saver-python/1.0"})
            with urlopen(req, timeout=timeout) as response:
                if response.status < 200 or response.status > 299:
                    return []
                data = response.read()
        except Exception:
            return []

        html = data.decode("utf-8", errors="ignore")
        return PackFetcher.parse_ans_filenames(html)

    @staticmethod
    def download_file(pack_url: str, filename: str, local_path: str, timeout: int = 30) -> bool:
        normalized = pack_url if pack_url.endswith("/") else f"{pack_url}/"
        raw_url = f"{normalized}raw/{quote(filename)}"
        try:
            req = Request(raw_url, headers={"User-Agent": "ansi-saver-python/1.0"})
            with urlopen(req, timeout=timeout) as response:
                if response.status < 200 or response.status > 299:
                    return False
                data = response.read()
        except Exception:
            return False

        Cache.write(data, local_path)
        return True

    @staticmethod
    def parse_ans_filenames(html: str) -> list[str]:
        seen: set[str] = set()
        names: list[str] = []
        for match in PackFetcher._ANS_PATTERN.finditer(html):
            name = match.group(1)
            if name not in seen:
                seen.add(name)
                names.append(name)
        return names
