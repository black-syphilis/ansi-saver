import tempfile
import unittest
from pathlib import Path

from ansi_saver.art_source import FolderSource
from ansi_saver.cache import Cache
from ansi_saver.pack_fetcher import PackFetcher


class CoreTests(unittest.TestCase):
    def test_parse_ans_filenames(self):
        html = '''
        <a href="/pack/a/raw/file.ans">file.ans</a>
        <a href="/pack/a/raw/logo.ICE">logo.ICE</a>
        <a href="/pack/a/raw/readme.txt">readme.txt</a>
        '''
        files = PackFetcher.parse_ans_filenames(html)
        self.assertEqual(files, ["file.ans", "logo.ICE"])

    def test_url_cache_path_is_deterministic(self):
        one = Cache.url_cache_path("https://example.com/art.ans")
        two = Cache.url_cache_path("https://example.com/art.ans")
        self.assertEqual(one, two)

    def test_folder_source_filters_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "a.ans").write_text("x")
            (tmp_path / "b.txt").write_text("x")
            (tmp_path / "c.ICE").write_text("x")

            paths = FolderSource(str(tmp_path)).load_art_paths()
            names = sorted(Path(p).name for p in paths)
            self.assertEqual(names, ["a.ans", "c.ICE"])


if __name__ == "__main__":
    unittest.main()
