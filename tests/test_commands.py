"""Тесты команд ls, cd, head, cal, uname на небольшой VFS."""
import unittest

from shell_emulator.shell import Shell
from shell_emulator.vfs import VFS
from support import run


def build_shell():
    """Создаёт оболочку с небольшой VFS для проверок."""
    vfs = VFS("test")
    vfs.add_file("/readme.txt", b"one\ntwo\nthree\n")
    vfs.add_file("/.hidden", b"x")
    vfs.add_file("/docs/a.txt", b"a\n")
    vfs.add_file("/bin.dat", bytes([0xFF, 0xFE, 0x00]))
    vfs.mkdir("/empty")
    return Shell(vfs)


class LsTest(unittest.TestCase):
    """Проверки ls."""

    def test_plain(self):
        """Скрытые файлы не показываются."""
        _, out, _ = run(build_shell(), "ls")
        self.assertEqual(out, "bin.dat  docs  empty  readme.txt\n")

    def test_all(self):
        """Ключ -a показывает скрытые файлы, . и .."""
        _, out, _ = run(build_shell(), "ls -a")
        self.assertTrue(out.startswith(".  ..  .hidden"))

    def test_long(self):
        """Ключ -l добавляет права и размер."""
        _, out, _ = run(build_shell(), "ls -l docs")
        self.assertEqual(out, "-rw-r--r-- 2 a.txt\n")

    def test_several_paths(self):
        """Для нескольких путей печатаются заголовки каталогов."""
        _, out, _ = run(build_shell(), "ls docs readme.txt")
        self.assertEqual(out, "readme.txt\n\ndocs:\na.txt\n")

    def test_missing(self):
        """Несуществующий путь — ошибка и код 1."""
        code, _, err = run(build_shell(), "ls nope")
        self.assertEqual(code, 1)
        self.assertIn("Нет такого файла", err)

    def test_bad_flag(self):
        """Неизвестный ключ — ошибка."""
        code, _, err = run(build_shell(), "ls -z")
        self.assertEqual(code, 1)
        self.assertIn("неверный ключ", err)


class CdTest(unittest.TestCase):
    """Проверки cd."""

    def test_change_directory(self):
        """cd меняет каталог и приглашение."""
        shell = build_shell()
        run(shell, "cd docs")
        self.assertEqual(shell.prompt, "test:/docs$ ")

    def test_back_and_dash(self):
        """cd .. поднимается, cd - возвращает и печатает путь."""
        shell = build_shell()
        run(shell, "cd docs")
        run(shell, "cd ..")
        _, out, _ = run(shell, "cd -")
        self.assertEqual(out, "/docs\n")

    def test_home_without_home_dir(self):
        """Без /home/user cd без аргументов ведёт в корень."""
        shell = build_shell()
        run(shell, "cd docs")
        run(shell, "cd")
        self.assertEqual(shell.cwd, "/")

    def test_errors(self):
        """Ошибки: нет каталога, файл вместо каталога, много аргументов."""
        shell = build_shell()
        self.assertIn("Нет такого", run(shell, "cd nope")[2])
        self.assertIn("Не является", run(shell, "cd readme.txt")[2])
        self.assertIn("слишком много", run(shell, "cd a b")[2])


class HeadTest(unittest.TestCase):
    """Проверки head."""

    def test_default(self):
        """Файл короче 10 строк выводится целиком."""
        _, out, _ = run(build_shell(), "head readme.txt")
        self.assertEqual(out, "one\ntwo\nthree\n")

    def test_count_forms(self):
        """-n 2 и -n2 равнозначны."""
        shell = build_shell()
        self.assertEqual(run(shell, "head -n 2 readme.txt")[1], "one\ntwo\n")
        self.assertEqual(run(shell, "head -n2 readme.txt")[1], "one\ntwo\n")

    def test_zero_lines(self):
        """-n 0 ничего не печатает."""
        self.assertEqual(run(build_shell(), "head -n 0 readme.txt")[1], "")

    def test_several_files(self):
        """Для нескольких файлов печатаются заголовки."""
        _, out, _ = run(build_shell(), "head -n 1 readme.txt docs/a.txt")
        self.assertEqual(out, "==> readme.txt <==\none\n\n"
                              "==> docs/a.txt <==\na\n")

    def test_binary_as_base64(self):
        """Двоичный файл показывается в base64."""
        _, out, _ = run(build_shell(), "head bin.dat")
        self.assertEqual(out, "//4A\n")

    def test_errors(self):
        """Ошибки: каталог, нет файла, нет аргументов, плохое число."""
        shell = build_shell()
        self.assertIn("Это каталог", run(shell, "head docs")[2])
        self.assertIn("Нет такого", run(shell, "head nope")[2])
        self.assertIn("не указан файл", run(shell, "head")[2])
        self.assertIn("неверное число", run(shell, "head -n x f")[2])
        self.assertIn("требует аргумент", run(shell, "head -n")[2])


class CalUnameTest(unittest.TestCase):
    """Проверки cal и uname."""

    def test_cal_month(self):
        """cal 2 2024 печатает февраль високосного года."""
        _, out, _ = run(build_shell(), "cal 2 2024")
        self.assertIn("February 2024", out)
        self.assertIn("25 26 27 28 29", out)

    def test_cal_year(self):
        """cal 2026 печатает все двенадцать месяцев."""
        _, out, _ = run(build_shell(), "cal 2026")
        self.assertIn("December", out)

    def test_cal_errors(self):
        """Неверный месяц, год и лишние аргументы."""
        shell = build_shell()
        self.assertIn("месяц", run(shell, "cal 13 2024")[2])
        self.assertIn("год", run(shell, "cal abc")[2])
        self.assertIn("слишком много", run(shell, "cal 1 2 3")[2])

    def test_uname(self):
        """uname по умолчанию печатает имя ядра, -a — все поля."""
        shell = build_shell()
        self.assertEqual(run(shell, "uname")[1], "Linux\n")
        _, out, _ = run(shell, "uname -a")
        self.assertEqual(out, "Linux test 6.1.0-emu #1 SMP Emulated "
                              "x86_64 GNU/Linux\n")
        self.assertEqual(run(shell, "uname -sr")[1], "Linux 6.1.0-emu\n")

    def test_uname_errors(self):
        """Неизвестный ключ и лишний операнд."""
        shell = build_shell()
        self.assertIn("неверный ключ", run(shell, "uname -z")[2])
        self.assertIn("лишний операнд", run(shell, "uname x")[2])
