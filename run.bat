@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  py -3.11 -m venv .venv 2>nul || python -m venv .venv
)

call ".venv\Scripts\activate.bat"
python -m pip install -q -r requirements.txt
python -m corte %*
