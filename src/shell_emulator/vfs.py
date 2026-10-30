"""Виртуальная файловая система, целиком хранящаяся в памяти."""
import posixpath
import zipfile
from pathlib import Path

ROOT = "/"
HOME_DIR = "/home/user"
HOME_ALIAS = "~"
DEFAULT_NAME = "vfs"
DIR_SIZE = 4096


class VFSError(Exception):
    """Ошибка создания или загрузки VFS."""


class Node:
    """Узел дерева: каталог (children) или файл (data)."""

    __slots__ = ("is_dir", "data", "children")

    def __init__(self, is_dir, data=b""):
        """Создаёт каталог или файл с содержимым data."""
        self.is_dir = is_dir
        self.data = data
        self.children = {} if is_dir else None

    @property
    def size(self):
        """Размер в байтах (для каталога — условный)."""
        return DIR_SIZE if self.is_dir else len(self.data)


class VFS:
    """Файловая система в памяти. Исходный архив не изменяется."""

    def __init__(self, name):
        """Создаёт пустую VFS с корневым каталогом."""
        self.name = name
        self.root = Node(True)

    @staticmethod
    def _parts(path):
        """Разбивает путь на непустые компоненты."""
        return [part for part in path.split("/") if part]

    def mkdir(self, path):
        """Создаёт каталог со всеми родителями и возвращает его узел."""
        node = self.root
        for part in self._parts(path):
            child = node.children.get(part)
            if child is None:
                child = Node(True)
                node.children[part] = child
            elif not child.is_dir:
                raise VFSError(f"'{part}' одновременно файл и каталог")
            node = child
        return node

    def add_file(self, path, data):
        """Создаёт файл (и каталоги над ним) с содержимым data."""
        parts = self._parts(path)
        if not parts:
            raise VFSError("пустое имя файла в архиве")
        parent = self.mkdir(ROOT.join(parts[:-1]))
        parent.children[parts[-1]] = Node(False, data)

    def lookup(self, abs_path):
        """Возвращает узел по абсолютному пути или None."""
        node = self.root
        for part in self._parts(abs_path):
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node

    @property
    def home(self):
        """Домашний каталог, а если его нет в VFS — корень."""
        node = self.lookup(HOME_DIR)
        return HOME_DIR if node is not None and node.is_dir else ROOT

    def resolve(self, cwd, path):
        """Превращает путь (с ~, . и ..) в абсолютный нормальный вид."""
        if path == HOME_ALIAS or path.startswith(HOME_ALIAS + ROOT):
            path = self.home + path[len(HOME_ALIAS):]
        full = posixpath.normpath(posixpath.join(cwd, path))
        return ROOT + full.lstrip(ROOT)

    def stats(self):
        """Возвращает пару (число файлов, число каталогов)."""
        files = dirs = 0
        stack = [self.root]
        while stack:
            for child in stack.pop().children.values():
                if child.is_dir:
                    dirs += 1
                    stack.append(child)
                else:
                    files += 1
        return files, dirs

    def _add_entry(self, bundle, info):
        """Переносит одну запись ZIP-архива в память."""
        name = info.filename.replace("\\", "/")
        full = posixpath.normpath(ROOT + name)
        if info.is_dir():
            self.mkdir(full)
        else:
            self.add_file(full, bundle.read(info))

    @classmethod
    def from_zip(cls, path):
        """Читает ZIP-архив целиком в память; сам архив не меняется."""
        archive = Path(path)
        vfs = cls(archive.stem)
        try:
            with zipfile.ZipFile(archive) as bundle:
                for info in bundle.infolist():
                    vfs._add_entry(bundle, info)
        except FileNotFoundError:
            raise VFSError(f"файл не найден: {path}") from None
        except zipfile.BadZipFile:
            raise VFSError(f"файл не является ZIP-архивом: {path}") from None
        except OSError as error:
            raise VFSError(str(error)) from error
        return vfs

    @classmethod
    def default(cls):
        """Создаёт небольшую VFS по умолчанию прямо в памяти."""
        vfs = cls(DEFAULT_NAME)
        readme = "Это VFS по умолчанию.\nОна живёт только в памяти.\n"
        vfs.add_file("/home/user/readme.txt", readme.encode("utf-8"))
        vfs.add_file("/home/user/docs/todo.txt", b"1. emulator\n2. tests\n")
        vfs.add_file("/etc/hostname", b"vfs\n")
        vfs.mkdir("/tmp")
        return vfs
