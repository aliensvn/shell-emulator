"""Тесты VFS: загрузка ZIP, поиск узлов, пути, ошибки."""
import tempfile
import unittest
import zipfile
from pathlib import Path

from shell_emulator.vfs import VFS, VFSError


class VFSTest(unittest.TestCase):
    """Проверки класса VFS."""

    def setUp(self):
        """Создаёт временный ZIP с вложенными папками и бинарным файлом."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.path = self.folder / "sample.zip"
        with zipfile.ZipFile(self.path, "w") as bundle:
            bundle.writestr("a/b/c/deep.txt", "hi")
            bundle.writestr("empty/", b"")
            bundle.writestr("bin.dat", bytes([0, 255]))

    def test_name_from_archive(self):
        """Имя VFS берётся из имени архива."""
        self.assertEqual(VFS.from_zip(self.path).name, "sample")

    def test_nested_file(self):
        """Файл на глубине трёх каталогов читается."""
        node = VFS.from_zip(self.path).lookup("/a/b/c/deep.txt")
        self.assertEqual(node.data, b"hi")

    def test_empty_directory(self):
        """Пустой каталог из архива сохраняется."""
        node = VFS.from_zip(self.path).lookup("/empty")
        self.assertTrue(node.is_dir)

    def test_binary_data_is_kept(self):
        """Двоичные данные не искажаются."""
        node = VFS.from_zip(self.path).lookup("/bin.dat")
        self.assertEqual(node.data, bytes([0, 255]))

    def test_archive_is_not_modified(self):
        """Исходный архив остаётся нетронутым."""
        before = self.path.read_bytes()
        VFS.from_zip(self.path)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in self.folder.iterdir()),
                         ["sample.zip"])

    def test_missing_archive(self):
        """Нет файла — VFSError."""
        with self.assertRaises(VFSError):
            VFS.from_zip(self.folder / "nope.zip")

    def test_not_a_zip(self):
        """Не ZIP — VFSError."""
        fake = self.folder / "fake.zip"
        fake.write_text("text", encoding="utf-8")
        with self.assertRaises(VFSError):
            VFS.from_zip(fake)

    def test_default_vfs(self):
        """VFS по умолчанию создаётся в памяти и содержит домашний каталог."""
        vfs = VFS.default()
        self.assertEqual(vfs.home, "/home/user")
        self.assertIsNotNone(vfs.lookup("/home/user/readme.txt"))

    def test_resolve(self):
        """resolve понимает .., ~ и не выходит выше корня."""
        vfs = VFS.default()
        self.assertEqual(vfs.resolve("/a/b", "../c"), "/a/c")
        self.assertEqual(vfs.resolve("/", ".."), "/")
        self.assertEqual(vfs.resolve("/", "~"), "/home/user")

    def test_stats(self):
        """stats считает файлы и каталоги."""
        files, dirs = VFS.from_zip(self.path).stats()
        self.assertEqual((files, dirs), (2, 4))
