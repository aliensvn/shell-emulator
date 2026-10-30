"""Тесты оболочки: разбор строки, ошибки, exit."""
import os
import unittest
from unittest import mock

from support import PROMPT, make_shell, run


class ShellTest(unittest.TestCase):
    """Проверки Shell.execute."""

    def test_stub_prints_name_and_args(self):
        """Заглушка выводит имя команды и аргументы."""
        code, out, _ = run(make_shell(), "ls -l /tmp")
        self.assertEqual(code, 0)
        self.assertIn("ls: аргументы = ['-l', '/tmp']", out)

    def test_stub_gets_expanded_variable(self):
        """Заглушка получает уже раскрытую переменную окружения."""
        with mock.patch.dict(os.environ, {"EMU_X": "val"}):
            _, out, _ = run(make_shell(), "cd $EMU_X")
        self.assertIn("['val']", out)

    def test_prompt_contains_vfs_name(self):
        """Приглашение содержит имя VFS."""
        self.assertEqual(make_shell().prompt, PROMPT)

    def test_unknown_command(self):
        """Неизвестная команда — код 1 и сообщение в stderr."""
        code, _, err = run(make_shell(), "foo bar")
        self.assertEqual(code, 1)
        self.assertIn("foo: команда не найдена", err)

    def test_parse_error(self):
        """Незакрытая кавычка не роняет эмулятор."""
        code, _, err = run(make_shell(), "ls 'oops")
        self.assertEqual(code, 1)
        self.assertIn("ошибка разбора", err)

    def test_empty_and_comment_lines(self):
        """Пустая строка и комментарий ничего не делают."""
        shell = make_shell()
        self.assertEqual(run(shell, "")[0], 0)
        self.assertEqual(run(shell, "# note")[1], "")

    def test_exit_default(self):
        """exit без аргументов завершает работу с кодом 0."""
        shell = make_shell()
        run(shell, "exit")
        self.assertFalse(shell.running)
        self.assertEqual(shell.exit_code, 0)

    def test_exit_code_from_env(self):
        """Код exit можно взять из переменной окружения."""
        shell = make_shell()
        with mock.patch.dict(os.environ, {"EMU_CODE": "3"}):
            run(shell, "exit $EMU_CODE")
        self.assertEqual(shell.exit_code, 3)

    def test_exit_bad_argument(self):
        """Нечисловой код — ошибка, эмулятор продолжает работу."""
        shell = make_shell()
        code, _, err = run(shell, "exit abc")
        self.assertEqual(code, 1)
        self.assertIn("числовой аргумент", err)
        self.assertTrue(shell.running)

    def test_exit_too_many_arguments(self):
        """Лишние аргументы exit — ошибка."""
        shell = make_shell()
        self.assertEqual(run(shell, "exit 1 2")[0], 1)
        self.assertTrue(shell.running)
