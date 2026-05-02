@echo off
chcp 65001 > nul
cd /d D:\desktop\VANMOLY-SYS-V3.0\backend
set PYTHONIOENCODING=utf-8
set PYTHONPATH=D:\desktop\VANMOLY-SYS-V3.0\backend
start "VANMOLY-FLASK" cmd /c "python -m flask --app app run --host=0.0.0.0 --port=8080"