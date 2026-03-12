import tempfile
import unittest
from pathlib import Path

from ansi_saver.art_source import FolderSource
from ansi_saver.cache import Cache
from ansi_saver.pack_fetcher import PackFetcher
from ansi_saver.viewer import load_paths, read_ansi_text


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

    def test_viewer_load_paths_from_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "b.ans").write_text("B")
            (tmp_path / "a.ans").write_text("A")
            paths = load_paths(folder=str(tmp_path), pack_url=None)
            self.assertEqual([Path(p).name for p in paths], ["a.ans", "b.ans"])

    def test_read_ansi_text_uses_latin1(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cp437ish.ans"
            path.write_bytes(bytes([0x41, 0xB0, 0x42]))
            content = read_ansi_text(path)
            self.assertEqual(len(content), 3)
            self.assertTrue(content.startswith("A"))


if __name__ == "__main__":
    unittest.main()
