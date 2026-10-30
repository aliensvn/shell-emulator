@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
set EMU_DEMO=docs
python tests\make_vfs.py >nul

echo === 1. VFS по умолчанию (в памяти) ===
(echo ls -l& echo cd home/user/docs& echo head todo.txt& echo exit) | python src\main.py
echo === 2. Минимальная VFS ===
python src\main.py --vfs tests\data\minimal.zip --script tests\scripts\vfs_minimal.emu
echo === 3. Несколько файлов ===
python src\main.py --vfs tests\data\files.zip --script tests\scripts\stage4_all.emu
echo === 4. Глубокая вложенность ===
python src\main.py --vfs tests\data\deep.zip --script tests\scripts\vfs_deep.emu
echo === 5. Ошибки: нет файла и не ZIP ===
python src\main.py --vfs tests\data\missing.zip
echo код возврата: %errorlevel%
python src\main.py --vfs tests\data\notazip.zip
echo код возврата: %errorlevel%
