"""Запуск эмулятора: python src/main.py [--vfs PATH] [--script PATH]."""
import sys

from shell_emulator.cli import main

if __name__ == "__main__":
    sys.exit(main())
