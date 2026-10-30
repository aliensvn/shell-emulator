#!/usr/bin/env bash
# Этап 3: варианты VFS
cd "$(dirname "$0")/../.." || exit 1
PY=${PYTHON:-python3}
export EMU_DEMO=docs
$PY tests/make_vfs.py >/dev/null

echo "=== 1. VFS по умолчанию (в памяти) ==="
printf 'ls\nexit\n' | $PY src/main.py
echo "=== 2. Минимальная VFS ==="
$PY src/main.py --vfs tests/data/minimal.zip --script tests/scripts/vfs_minimal.emu
echo "=== 3. Несколько файлов ==="
$PY src/main.py --vfs tests/data/files.zip --script tests/scripts/stage3_all.emu
echo "=== 4. Глубокая вложенность ==="
$PY src/main.py --vfs tests/data/deep.zip --script tests/scripts/vfs_deep.emu
echo "=== 5. Ошибки: нет файла и не ZIP ==="
$PY src/main.py --vfs tests/data/missing.zip; echo "код возврата: $?"
$PY src/main.py --vfs tests/data/notazip.zip; echo "код возврата: $?"
