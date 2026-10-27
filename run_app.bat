@echo off
title RaceEngineer AI - Setup and Launch
cd /d "%~dp0"
echo ==========================================
echo       RaceEngineer AI - Setup
echo ==========================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10 or newer from https://www.python.org/downloads/
  echo During installation, tick "Add Python to PATH".
  pause
  exit /b 1
)
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Package installation failed. Check your internet connection and Python installation.
  pause
  exit /b 1
)
echo Starting RaceEngineer AI...
python -m streamlit run app.py
pause
