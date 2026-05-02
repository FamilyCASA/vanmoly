@echo off
chcp 65001 >nul
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python3.exe 2>nul
timeout /t 3 >nul
cd /d D:\desktop\VANMOLY-SYS-V3.0\backend
start /B python run_waitress.py
echo Backend restarted on port 8080
