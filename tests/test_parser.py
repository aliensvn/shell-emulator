"""Тесты разбора строки: переменные окружения и токены."""
import unittest

from shell_emulator.parser import (CommandError, expand_env, is_number,
                                   split_flags, tokenize)

ENV = {"HOME": "/home/me", "NAME": "x"}


class ExpandEnvTest(unittest.TestCase):
    """Проверки expand_env."""

    def test_plain_variable(self):
        """$VAR заменяется значением."""
        self.assertEqual(expand_env("cd $HOME", ENV), "cd /home/me")

    def test_braces(self):
        """${VAR} позволяет дописать текст сразу после имени."""
        self.assertEqual(expand_env("${NAME}yz", ENV), "xyz")

    def test_unknown_is_empty(self):
        """Неизвестная переменная даёт пустую строку."""
        self.assertEqual(expand_env("a $NOPE b", ENV), "a  b")

    def test_single_quotes_protect(self):
        """В одинарных кавычках переменные не раскрываются."""
        self.assertEqual(expand_env("'$HOME' $HOME", ENV),
                         "'$HOME' /home/me")


class TokenizeTest(unittest.TestCase):
    """Проверки tokenize и is_number."""

    def test_quotes_and_spaces(self):
        """Кавычки собирают слова с пробелами в один токен."""
        self.assertEqual(tokenize('ls -l "a b"'), ["ls", "-l", "a b"])

    def test_comment_is_dropped(self):
        """Всё после # отбрасывается."""
        self.assertEqual(tokenize("ls  # list"), ["ls"])

    def test_unclosed_quote(self):
        """Незакрытая кавычка — ValueError."""
        with self.assertRaises(ValueError):
            tokenize("ls 'oops")

    def test_is_number(self):
        """is_number принимает только ASCII-цифры."""
        self.assertTrue(is_number("42"))
        self.assertFalse(is_number("4x"))
        self.assertFalse(is_number(""))


class SplitFlagsTest(unittest.TestCase):
    """Проверки split_flags."""

    def test_combined_flags(self):
        """-la раскрывается в два ключа."""
        flags, rest = split_flags(["-la", "dir"], "la", "ls")
        self.assertEqual(flags, {"l", "a"})
        self.assertEqual(rest, ["dir"])

    def test_double_dash(self):
        """После -- всё считается операндами."""
        flags, rest = split_flags(["--", "-l"], "l", "ls")
        self.assertEqual(flags, set())
        self.assertEqual(rest, ["-l"])

    def test_unknown_flag(self):
        """Неизвестный ключ вызывает CommandError."""
        with self.assertRaises(CommandError):
            split_flags(["-z"], "la", "ls")
