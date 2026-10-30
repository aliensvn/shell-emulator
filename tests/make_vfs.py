"""Создаёт тестовые ZIP-архивы для VFS в папке tests/data/."""
import zipfile
from pathlib import Path

OUT = Path(__file__).parent / "data"
NUMBER_LINES = 20
PNG_HEAD = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
BINARY = (PNG_HEAD + bytes([0xFF, 0xFE, 0x00, 0x01])) * NUMBER_LINES


def build(name, files, dirs=()):
    """Собирает архив name из словаря файлов и списка пустых каталогов."""
    with zipfile.ZipFile(OUT / name, "w", zipfile.ZIP_DEFLATED) as bundle:
        for folder in dirs:
            bundle.writestr(folder.rstrip("/") + "/", b"")
        for path, data in files.items():
            bundle.writestr(path, data)


def build_minimal():
    """Минимальная VFS: один файл."""
    build("minimal.zip", {"hello.txt": "Hello, VFS!\n".encode("utf-8")})


def build_files():
    """VFS с несколькими файлами, скрытым и двоичным."""
    numbers = "".join(f"line {i}\n" for i in range(1, NUMBER_LINES + 1))
    text = "Первая строка\nВторая строка\nТретья строка\n"
    build("files.zip", {
        "readme.txt": text.encode("utf-8"),
        "numbers.txt": numbers.encode("utf-8"),
        ".hidden": b"secret\n",
        "logo.bin": BINARY,
        "docs/guide.txt": b"guide line 1\nguide line 2\n",
    }, dirs=["empty_dir", "docs"])


def build_deep():
    """VFS с вложенностью в пять уровней."""
    report = "Q3: всё хорошо\nвыручка выросла\n".encode("utf-8")
    build("deep.zip", {
        "home/user/docs/work/reports/2026/q3.txt": report,
        "home/user/docs/work/notes.txt": b"note 1\nnote 2\nnote 3\n",
        "home/user/readme.txt": b"deep vfs\n",
        "etc/config/app/settings.ini": b"[main]\ndebug=1\n",
    }, dirs=["home/user/music"])


def main():
    """Создаёт все тестовые архивы и файл, не являющийся архивом."""
    OUT.mkdir(exist_ok=True)
    build_minimal()
    build_files()
    build_deep()
    (OUT / "notazip.zip").write_text("это не архив\n", encoding="utf-8")
    print("Тестовые архивы созданы в", OUT)


if __name__ == "__main__":
    main()
