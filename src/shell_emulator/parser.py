"""Разбор строки эмулятора: переменные окружения и токены."""
import os
import re
import shlex

TOKEN_PATTERN = re.compile(r"('[^']*')|\$(\w+)|\$\{(\w+)\}")


def is_number(text):
    """Возвращает True, если строка состоит только из ASCII-цифр."""
    return text.isascii() and text.isdigit()


def expand_env(line, environ=None):
    """Раскрывает $VAR и ${VAR} в строке.

    Текст в одинарных кавычках не меняется. Неизвестная переменная
    заменяется пустой строкой, как в bash.
    """
    env = os.environ if environ is None else environ

    def substitute(match):
        """Возвращает замену для одного найденного фрагмента."""
        if match.group(1):
            return match.group(1)
        return env.get(match.group(2) or match.group(3), "")

    return TOKEN_PATTERN.sub(substitute, line)


def tokenize(line):
    """Раскрывает переменные и режет строку на слова.

    Символ # начинает комментарий. При незакрытой кавычке
    бросает ValueError.
    """
    return shlex.split(expand_env(line), comments=True)
