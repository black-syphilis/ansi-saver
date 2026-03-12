from __future__ import annotations

import hashlib
import os
from pathlib import Path


class Cache:
    @staticmethod
    def _base_path() -> Path:
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return Path(local) / "AnsiSaver"
        xdg = os.environ.get("XDG_CACHE_HOME")
        if xdg:
            return Path(xdg) / "AnsiSaver"
        return Path.home() / ".cache" / "AnsiSaver"

    @classmethod
    def ans_path(cls, pack: str, file: str) -> Path:
        return cls._base_path() / "packs" / pack / file

    @staticmethod
    def png_path(ans_path: str | Path) -> Path:
        return Path(ans_path).with_suffix(".png")

    @classmethod
    def url_cache_path(cls, url_string: str) -> Path:
        digest = hashlib.sha256(url_string.encode("utf-8")).hexdigest()
        return cls._base_path() / "urls" / f"{digest}.ans"

    @staticmethod
    def read(path: str | Path) -> bytes | None:
        p = Path(path)
        if not p.exists():
            return None
        return p.read_bytes()

    @staticmethod
    def write(data: bytes, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    @staticmethod
    def exists(path: str | Path) -> bool:
        return Path(path).exists()

    @classmethod
    def clear_packs(cls) -> None:
        packs = cls._base_path() / "packs"
        if packs.exists():
            for child in packs.rglob("*"):
                if child.is_file():
                    child.unlink()
            for child in sorted(packs.rglob("*"), reverse=True):
                if child.is_dir():
                    child.rmdir()
            packs.rmdir()

    @classmethod
    def clear_all(cls) -> None:
        base = cls._base_path()
        if not base.exists():
            return
        for child in base.rglob("*"):
            if child.is_file():
                child.unlink()
        for child in sorted(base.rglob("*"), reverse=True):
            if child.is_dir():
                child.rmdir()
        base.rmdir()
