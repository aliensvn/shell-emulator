"""Точка входа эмулятора: интерактивный цикл (этап 1)."""
import sys

from shell_emulator.shell import Shell


def configure_output():
    """Переключает stdout и stderr в UTF-8, если это возможно."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            continue


def read_line(shell):
    """Читает строку ввода; None означает конец ввода (Ctrl+D)."""
    try:
        return input(shell.prompt)
    except EOFError:
        print()
        return None
    except KeyboardInterrupt:
        print()
        return ""


def interactive(shell):
    """Крутит цикл «приглашение — ввод — выполнение» до exit или EOF."""
    while shell.running:
        line = read_line(shell)
        if line is None:
            break
        shell.execute(line)
        if not shell.running and not sys.stdin.isatty():
            print()


def main():
    """Запускает эмулятор и возвращает код завершения."""
    configure_output()
    shell = Shell()
    interactive(shell)
    return shell.exit_code
