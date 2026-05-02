@echo off
cd /d D:\desktop\VANMOLY-SYS-V3.0\backend
python -c "from waitress import serve; from app import create_app; serve(create_app(), host='0.0.0.0', port=8000, threads=4)"
pause