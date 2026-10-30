#!/usr/bin/env bash
# Этап 2: проверка параметров командной строки
cd "$(dirname "$0")/../.." || exit 1
PY=${PYTHON:-python3}
export EMU_DEMO=docs

echo "=== 1. Без параметров ==="
echo exit | $PY src/main.py
echo "=== 2. Только --script ==="
$PY src/main.py --script tests/scripts/stage2_demo.emu
echo "=== 3. Только --vfs ==="
echo exit | $PY src/main.py --vfs data/myvfs.zip
echo "=== 4. Оба параметра ==="
$PY src/main.py --vfs data/myvfs.zip --script tests/scripts/stage2_demo.emu
echo "=== 5. Ошибка: скрипт не найден ==="
$PY src/main.py --script tests/scripts/no_such.emu; echo "код возврата: $?"
echo "=== 6. Ошибка: неизвестный параметр ==="
$PY src/main.py --bogus; echo "код возврата: $?"
