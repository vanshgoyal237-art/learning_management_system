@echo off
setlocal
cd /d "%~dp0"
title LMS - first-time setup
echo ============================================================
echo   LMS first-time setup  (run this ONCE; later just use start.bat)
echo   Before you begin: MySQL must be installed and running.
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python from python.org and tick "Add python.exe to PATH", then run this again.
  goto :fail
)

if not exist venv\Scripts\python.exe (
  echo [1/5] Creating the virtual environment...
  python -m venv venv
  if errorlevel 1 goto :fail
) else (
  echo [1/5] Virtual environment already exists.
)

echo [2/5] Installing packages (a few minutes the first time)...
venv\Scripts\python.exe -m pip install --upgrade pip >nul
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo [3/5] Creating the database and your .env file (you will be asked for the MySQL root password)...
venv\Scripts\python.exe scripts\setup_db.py
if errorlevel 1 goto :fail

echo [4/5] Checking the prediction model...
if not exist model\artifacts\rf_model.pkl (
  venv\Scripts\python.exe -m model.train_model
  if errorlevel 1 goto :fail
) else (
  echo       Model files are already here.
)

echo [5/5] Loading demo teachers, students, subjects and timetable...
venv\Scripts\python.exe scripts\seed_demo.py --reset
if errorlevel 1 goto :fail

echo.
echo ============================================================
echo   All done.  Now double-click  start.bat  to open the website.
echo   Admin login:   admin@lms.test   /   Admin@12345
echo ============================================================
pause
exit /b 0

:fail
echo.
echo *** Setup stopped because of the message above. Read it, fix it, and run setup.bat again. ***
pause
exit /b 1
