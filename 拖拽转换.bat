@echo off
rem Drag a PNG onto this file to make a one-shot bouncy GIF.
if "%~1"=="" (
  echo Usage: drag a PNG file onto this bat.
  pause
  exit /b 1
)
python "%~dp0qbounce.py" "%~1"
pause
