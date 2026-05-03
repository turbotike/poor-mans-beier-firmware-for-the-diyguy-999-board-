@echo off
REM Double-click to launch Poor Man's Beier.
title Poor Man's Beier
cd /d "%~dp0"
python flasher_server.py
if errorlevel 1 (
  echo.
  echo Could not start. Make sure Python 3 is installed and on PATH:
  echo   https://www.python.org/downloads/
  pause
)
