"""Общие помощники для тестов."""
import io
from contextlib import redirect_stderr, redirect_stdout

from shell_emulator.shell import Shell
from shell_emulator.vfs import VFS

PROMPT = "vfs$ "


def make_shell():
    """Создаёт оболочку с VFS по умолчанию."""
    return Shell(VFS.default())


def run(shell, line):
    """Выполняет строку и возвращает (код, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = shell.execute(line)
    return code, out.getvalue(), err.getvalue()
