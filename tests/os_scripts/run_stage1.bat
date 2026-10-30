@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
if not defined HOME set HOME=%USERPROFILE%
(
echo ls
echo ls -l /tmp "dir with space"
echo cd $HOME
echo cd '$HOME'
echo cd $NO_SUCH_VAR
echo foo bar
echo exit
) | python src\main.py
