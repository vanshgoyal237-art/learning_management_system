@echo off
setlocal
cd /d "%~dp0"
title LMS website (keep this window open)

if not exist venv\Scripts\python.exe (
  echo First-time setup has not been done yet - starting it now...
  call setup.bat
  exit /b
)

echo ============================================================
echo   Starting the website at  http://127.0.0.1:5000
echo   Keep this window open while you use the site.
echo   Press Ctrl+C here to stop it.
echo ============================================================
start "" /min cmd /c "timeout /t 4 /nobreak >nul && start http://127.0.0.1:5000"
venv\Scripts\python.exe -m flask --app app run --debug
echo.
echo The website has stopped. If you saw a red error above, copy it and send it to your helper.
pause
