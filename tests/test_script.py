"""Тесты стартового скрипта: показ ввода, комментарии, exit."""
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from shell_emulator.cli import run_script, start_script
from support import PROMPT, make_shell

SCRIPT = "# comment\n\nls\nfoo\nexit\nls after exit\n"


class RunScriptTest(unittest.TestCase):
    """Проверки run_script и start_script."""

    def setUp(self):
        """Создаёт временный файл со скриптом."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "demo.emu"
        self.path.write_text(SCRIPT, encoding="utf-8")

    def run_it(self):
        """Выполняет скрипт и возвращает перехваченный вывод."""
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            run_script(make_shell(), self.path)
        return out.getvalue()

    def test_input_is_echoed_with_prompt(self):
        """Команды показываются вместе с приглашением."""
        self.assertIn(PROMPT + "ls", self.run_it())

    def test_comment_is_shown_as_is(self):
        """Комментарии печатаются без приглашения."""
        self.assertIn("# comment\n", self.run_it())

    def test_stops_after_exit(self):
        """Строки после exit не выполняются."""
        self.assertNotIn("after exit", self.run_it())

    def test_missing_script(self):
        """Отсутствующий скрипт даёт False, а не исключение."""
        with redirect_stderr(io.StringIO()):
            result = start_script(make_shell(), "no_such_file.emu")
        self.assertFalse(result)
