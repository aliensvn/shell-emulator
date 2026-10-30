#!/usr/bin/env bash
# Этап 1: демонстрация REPL (ввод через pipe)
cd "$(dirname "$0")/../.." || exit 1
PY=${PYTHON:-python3}
cat <<'IN' | $PY src/main.py
ls
ls -l /tmp "dir with space"
cd $HOME
cd '$HOME'
cd $NO_SUCH_VAR
foo bar
ls 'unclosed
exit
IN
