"""Точка входа эмулятора: параметры, стартовый скрипт и REPL."""
import argparse
import sys
from pathlib import Path

from shell_emulator.shell import Shell

COMMENT_PREFIX = "#"
VFS_HELP = "путь к физическому расположению VFS"
VFS_UNSET = "<не задан>"


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


def build_parser():
    """Создаёт разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="emulator", description="Эмулятор оболочки UNIX-подобной ОС")
    parser.add_argument("--vfs", metavar="PATH", help=VFS_HELP)
    parser.add_argument("--script", metavar="PATH", help="стартовый скрипт")
    return parser


def print_debug(args):
    """Печатает все заданные параметры запуска."""
    print("[debug] Параметры запуска:")
    print(f"[debug]   --vfs    = {args.vfs or VFS_UNSET}")
    print(f"[debug]   --script = {args.script or '<не задан>'}")


def run_script(shell, path):
    """Выполняет скрипт, показывая ввод и вывод как живой диалог."""
    with open(path, encoding="utf-8-sig") as handle:
        lines = handle.read().splitlines()
    for raw in lines:
        if not raw.strip():
            continue
        if raw.lstrip().startswith(COMMENT_PREFIX):
            print(raw)
            continue
        print(shell.prompt + raw)
        shell.execute(raw)
        if not shell.running:
            break


def start_script(shell, path):
    """Запускает скрипт; при ошибке чтения печатает её и даёт False."""
    try:
        run_script(shell, path)
    except OSError as error:
        print(f"emulator: не удалось прочитать скрипт: {error}",
              file=sys.stderr)
        return False
    return True


def main(argv=None):
    """Запускает эмулятор и возвращает код завершения."""
    configure_output()
    args = build_parser().parse_args(argv)
    print_debug(args)
    shell = Shell(Path(args.vfs).stem if args.vfs else "vfs")
    if args.script and not start_script(shell, args.script):
        return 1
    if shell.running:
        interactive(shell)
    return shell.exit_code
