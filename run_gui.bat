@echo off
REM Script to run the PHAI GUI application on Windows

cd /d "%~dp0"
call PHAIenv\Scripts\activate.bat
python gui_app.py


