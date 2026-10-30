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


END_OF_FLAGS = "--"


class CommandError(Exception):
    """Ошибка выполнения команды; текст готов к показу пользователю."""


def check_flags(letters, allowed, command):
    """Проверяет буквы ключей и возвращает их множество."""
    for letter in letters:
        if letter not in allowed:
            raise CommandError(f"{command}: неверный ключ -- '{letter}'")
    return set(letters)


def split_flags(args, allowed, command):
    """Делит аргументы на множество ключей и список операндов.

    Ключи вида -la раскрываются в буквы, «--» заканчивает разбор ключей.
    Неизвестная буква вызывает CommandError.
    """
    flags, operands = set(), []
    for index, arg in enumerate(args):
        if arg == END_OF_FLAGS:
            operands.extend(args[index + 1:])
            break
        if arg.startswith("-") and arg != "-":
            flags |= check_flags(arg[1:], allowed, command)
        else:
            operands.append(arg)
    return flags, operands
