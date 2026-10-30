"""Вывод сообщений об ошибках."""
import sys


def report_error(message):
    """Печатает сообщение об ошибке в stderr и возвращает код 1."""
    sys.stdout.flush()
    print(message, file=sys.stderr, flush=True)
    return 1
