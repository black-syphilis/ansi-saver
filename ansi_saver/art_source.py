from __future__ import annotations

from pathlib import Path
from urllib.request import Request, urlopen

from .cache import Cache
from .pack_fetcher import PackFetcher


class FolderSource:
    _EXTENSIONS = {"ans", "ansi", "asc", "diz", "ice", "bin", "xb", "pcb", "adf"}

    def __init__(self, folder_path: str) -> None:
        self.folder_path = Path(folder_path)

    def load_art_paths(self) -> list[str]:
        if not self.folder_path.exists() or not self.folder_path.is_dir():
            return []
        return [
            str(path)
            for path in self.folder_path.iterdir()
            if path.is_file() and path.suffix.lower().lstrip(".") in self._EXTENSIONS
        ]


class PackSource:
    def __init__(self, pack_url: str) -> None:
        self.pack_url = pack_url

    def load_art_paths(self) -> list[str]:
        pack_name = self._extract_pack_name(self.pack_url)
        filenames = PackFetcher.fetch_file_list(self.pack_url)
        if not filenames:
            return []

        local_paths: list[str] = []
        for filename in filenames:
            local_path = Cache.ans_path(pack=pack_name, file=filename)
            if Cache.exists(local_path):
                local_paths.append(str(local_path))
                continue
            success = PackFetcher.download_file(self.pack_url, filename, str(local_path))
            if success:
                local_paths.append(str(local_path))
        return local_paths

    @staticmethod
    def _extract_pack_name(url: str) -> str:
        trimmed = url[:-1] if url.endswith("/") else url
        return trimmed.rsplit("/", maxsplit=1)[-1]


class URLSource:
    def __init__(self, file_urls: list[str]) -> None:
        self.file_urls = file_urls

    def load_art_paths(self) -> list[str]:
        local_paths: list[str] = []
        for url in self.file_urls:
            local_path = Cache.url_cache_path(url)
            if Cache.exists(local_path):
                local_paths.append(str(local_path))
                continue
            try:
                req = Request(url, headers={"User-Agent": "ansi-saver-python/1.0"})
                with urlopen(req, timeout=30) as response:
                    if response.status < 200 or response.status > 299:
                        continue
                    data = response.read()
            except Exception:
                continue

            Cache.write(data, local_path)
            local_paths.append(str(local_path))
        return local_paths
