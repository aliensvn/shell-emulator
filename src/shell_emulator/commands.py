"""Команды эмулятора: ls, cd, head, cal, uname."""
import base64
import calendar
import datetime

from shell_emulator.output import report_error
from shell_emulator.parser import CommandError, is_number, split_flags

SINGLE = 1
MAX_CD_ARGS = 1
MAX_CAL_ARGS = 2
DEFAULT_LINES = 10
MIN_MONTH, MAX_MONTH = 1, 12
MIN_YEAR, MAX_YEAR = 1, 9999
YEAR_COLUMNS = 3
LS_FLAGS = "la"
UNAME_ORDER = "snrvmo"
NO_FILE = "Нет такого файла или каталога"
DIR_MODE = "drwxr-xr-x"
FILE_MODE = "-rw-r--r--"


def collect_targets(shell, paths):
    """Делит пути ls на файлы и каталоги, ошибки печатает сразу."""
    files, dirs, status = [], [], 0
    for path in paths:
        node = shell.vfs.lookup(shell.vfs.resolve(shell.cwd, path))
        if node is None:
            status = report_error(
                f"ls: невозможно получить доступ к '{path}': {NO_FILE}")
        elif node.is_dir:
            dirs.append((path, node))
        else:
            files.append((path, node))
    return files, dirs, status


def format_entries(entries, long_format):
    """Форматирует список (имя, узел) в одну строку или в таблицу."""
    if not long_format:
        return "  ".join(name for name, _ in entries)
    rows = [(DIR_MODE if node.is_dir else FILE_MODE, node.size, name)
            for name, node in entries]
    width = max(len(str(size)) for _, size, _ in rows)
    return "\n".join(f"{mode} {size:>{width}} {name}"
                     for mode, size, name in rows)


def dir_entries(node, show_all):
    """Отсортированное содержимое каталога; скрытые — только с -a."""
    entries = sorted(
        (name, child) for name, child in node.children.items()
        if show_all or not name.startswith("."))
    if show_all:
        entries = [(".", node), ("..", node)] + entries
    return entries


def format_dir(name, node, flags, with_header):
    """Текст листинга одного каталога (с заголовком «имя:» по запросу)."""
    entries = dir_entries(node, "a" in flags)
    text = format_entries(entries, "l" in flags) if entries else ""
    if with_header:
        text = f"{name}:" + (f"\n{text}" if text else "")
    return text


def cmd_ls(shell, args):
    """ls [-l] [-a] [путь...] — список файлов и каталогов."""
    flags, paths = split_flags(args, LS_FLAGS, "ls")
    targets = paths or ["."]
    files, dirs, status = collect_targets(shell, targets)
    blocks = [format_entries(files, "l" in flags)] if files else []
    with_header = len(targets) > SINGLE
    for name, node in dirs:
        blocks.append(format_dir(name, node, flags, with_header))
    text = "\n\n".join(block for block in blocks if block)
    if text:
        print(text)
    return status


def directory_error(vfs, full, target):
    """Текст ошибки для cd или None, если в каталог можно перейти."""
    node = vfs.lookup(full)
    if node is None:
        return f"cd: {target}: {NO_FILE}"
    if not node.is_dir:
        return f"cd: {target}: Не является каталогом"
    return None


def cmd_cd(shell, args):
    """cd [путь | - | ~] — смена текущего каталога."""
    if len(args) > MAX_CD_ARGS:
        return report_error("cd: слишком много аргументов")
    target = args[0] if args else "~"
    full = shell.oldpwd if target == "-" else shell.vfs.resolve(
        shell.cwd, target)
    error = directory_error(shell.vfs, full, target)
    if error:
        return report_error(error)
    if target == "-":
        print(full)
    shell.oldpwd, shell.cwd = shell.cwd, full
    return 0


def parse_count(value):
    """Преобразует значение ключа -n в число строк."""
    if not is_number(value):
        raise CommandError(f"head: неверное число строк: '{value}'")
    return int(value)


def read_count_value(args, index):
    """Читает значение -n (-n 5 или -n5); возвращает (значение, индекс)."""
    if args[index] != "-n":
        return args[index][2:], index + 1
    rest = args[index + 1:]
    if not rest:
        raise CommandError("head: опция требует аргумент -- 'n'")
    return rest[0], index + 2


def parse_head_args(args):
    """Разбирает аргументы head и возвращает (число строк, файлы)."""
    count, files, index = DEFAULT_LINES, [], 0
    while index < len(args):
        arg = args[index]
        if arg == "--":
            files.extend(args[index + 1:])
            break
        if arg.startswith("-n"):
            value, index = read_count_value(args, index)
            count = parse_count(value)
        elif arg.startswith("-") and arg != "-":
            raise CommandError(f"head: неверный ключ -- '{arg[1:]}'")
        else:
            files.append(arg)
            index += 1
    return count, files


def load_lines(shell, name):
    """Возвращает строки файла; двоичные данные — в виде base64."""
    node = shell.vfs.lookup(shell.vfs.resolve(shell.cwd, name))
    if node is None:
        raise CommandError(f"head: невозможно открыть '{name}': {NO_FILE}")
    if node.is_dir:
        raise CommandError(f"head: ошибка чтения '{name}': Это каталог")
    try:
        return node.data.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return base64.encodebytes(node.data).decode("ascii").splitlines()


def cmd_head(shell, args):
    """head [-n N] файл... — первые строки файлов (по умолчанию 10)."""
    count, files = parse_head_args(args)
    if not files:
        return report_error("head: не указан файл (stdin не поддерживается)")
    status = 0
    for position, name in enumerate(files):
        try:
            lines = load_lines(shell, name)
        except CommandError as error:
            status = report_error(str(error))
            continue
        if len(files) > SINGLE:
            print(("\n" if position else "") + f"==> {name} <==")
        for line in lines[:count]:
            print(line)
    return status


def parse_number(text, what, low, high):
    """Проверяет число в диапазоне [low, high] и возвращает его."""
    if not (is_number(text) and low <= int(text) <= high):
        raise CommandError(f"cal: неверный {what}: '{text}'")
    return int(text)


def render_calendar(args):
    """Строит текст календаря по аргументам cal."""
    sunday_first = calendar.TextCalendar(calendar.SUNDAY)
    if not args:
        today = datetime.date.today()
        return sunday_first.formatmonth(today.year, today.month)
    if len(args) == SINGLE:
        year = parse_number(args[0], "год", MIN_YEAR, MAX_YEAR)
        return sunday_first.formatyear(year, m=YEAR_COLUMNS)
    month = parse_number(args[0], "месяц", MIN_MONTH, MAX_MONTH)
    year = parse_number(args[1], "год", MIN_YEAR, MAX_YEAR)
    return sunday_first.formatmonth(year, month)


def cmd_cal(shell, args):
    """cal [[месяц] год] — календарь месяца или года."""
    if len(args) > MAX_CAL_ARGS:
        return report_error("cal: слишком много аргументов")
    text = render_calendar(args)
    print("\n".join(line.rstrip() for line in text.splitlines()))
    return 0


def cmd_uname(shell, args):
    """uname [-snrvmoa] — сведения о (воображаемой) системе."""
    flags, extra = split_flags(args, UNAME_ORDER + "a", "uname")
    if extra:
        return report_error(f"uname: лишний операнд '{extra[0]}'")
    info = {"s": "Linux", "n": shell.vfs.name, "r": "6.1.0-emu",
            "v": "#1 SMP Emulated", "m": "x86_64", "o": "GNU/Linux"}
    if "a" in flags:
        flags = set(UNAME_ORDER)
    flags = flags or {"s"}
    print(" ".join(info[key] for key in UNAME_ORDER if key in flags))
    return 0


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "head": cmd_head,
    "cal": cmd_cal,
    "uname": cmd_uname,
}
