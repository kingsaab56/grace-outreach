@echo off
title Grace Outreach Assistant V1.0 - King Saab Terminal Edition
chcp 65001 >nul
cd /d "E:\Grace Outreach Assistant"
python "E:\Grace Outreach Assistant\original_terminal_main.py"
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error. Press any key to close.
    pause >nul
)
