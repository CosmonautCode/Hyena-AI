@echo off

pip install uv

REM Activate Python environment if using venv
call venv\Scripts\activate.bat

REM Sync UV environment (if uv is a custom tool)
uv sync


REM Run the app
uv run -m app.app

REM Keep the window open (optional)
pause
