"""Оболочка эмулятора: разбор строки и запуск команд."""
from shell_emulator.output import report_error
from shell_emulator.parser import is_number, tokenize

EXIT_CODE_MOD = 256
MAX_EXIT_ARGS = 1


def parse_exit_code(args):
    """Возвращает код из аргументов exit или бросает ValueError."""
    if not args:
        return 0
    if not is_number(args[0]):
        raise ValueError(f"exit: {args[0]}: требуется числовой аргумент")
    return int(args[0]) % EXIT_CODE_MOD


def cmd_exit(shell, args):
    """Завершает работу эмулятора; необязательный аргумент — код."""
    if len(args) > MAX_EXIT_ARGS:
        return report_error("exit: слишком много аргументов")
    try:
        code = parse_exit_code(args)
    except ValueError as error:
        return report_error(str(error))
    shell.exit_code = code
    shell.running = False
    return code


def stub(name):
    """Создаёт команду-заглушку, печатающую своё имя и аргументы."""

    def command(shell, args):
        """Печатает имя команды и список её аргументов."""
        print(f"{name}: аргументы = {args}")
        return 0

    return command


class Shell:
    """Состояние оболочки и выполнение введённых строк."""

    def __init__(self, vfs):
        """Создаёт оболочку над виртуальной файловой системой."""
        self.vfs = vfs
        self.running = True
        self.exit_code = 0
        self.commands = {
            "ls": stub("ls"),
            "cd": stub("cd"),
            "exit": cmd_exit,
        }

    @property
    def prompt(self):
        """Текст приглашения к вводу."""
        return f"{self.vfs.name}$ "

    def execute(self, line):
        """Выполняет одну строку и возвращает код завершения."""
        try:
            argv = tokenize(line)
        except ValueError as error:
            return report_error(f"emulator: ошибка разбора команды: {error}")
        if not argv:
            return 0
        handler = self.commands.get(argv[0])
        if handler is None:
            return report_error(f"{argv[0]}: команда не найдена")
        return handler(self, argv[1:])
