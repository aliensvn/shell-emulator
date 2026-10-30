@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
set EMU_DEMO=docs

echo === 1. Без параметров ===
echo exit | python src\main.py
echo === 2. Только --script ===
python src\main.py --script tests\scripts\stage2_demo.emu
echo === 3. Только --vfs ===
echo exit | python src\main.py --vfs data\myvfs.zip
echo === 4. Оба параметра ===
python src\main.py --vfs data\myvfs.zip --script tests\scripts\stage2_demo.emu
echo === 5. Ошибка: скрипт не найден ===
python src\main.py --script tests\scripts\no_such.emu
echo код возврата: %errorlevel%
echo === 6. Ошибка: неизвестный параметр ===
python src\main.py --bogus
echo код возврата: %errorlevel%
