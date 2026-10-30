"""Общие помощники для тестов."""
import io
from contextlib import redirect_stderr, redirect_stdout

from shell_emulator.shell import Shell

PROMPT = "vfs$ "


def make_shell():
    """Создаёт оболочку для тестов."""
    return Shell()


def run(shell, line):
    """Выполняет строку и возвращает (код, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = shell.execute(line)
    return code, out.getvalue(), err.getvalue()
