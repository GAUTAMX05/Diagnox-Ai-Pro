@echo off
cd /d "%~dp0"
echo Stopping old servers on port 5000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
echo Starting DiagnoX AI Pro...
python app.py
pause
