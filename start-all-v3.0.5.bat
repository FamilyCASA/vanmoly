@echo off
chcp 65001 >nul
title Vanmoly V3.0.5 Startup
color 0A

echo ==========================================
echo    Vanmoly System V3.0.5
echo    One-Click Startup
echo ==========================================
echo.

:: Set paths
set "PROJECT_DIR=D:\desktop\VANMOLY-SYS-V3.0"
set "BACKEND_DIR=%PROJECT_DIR%\backend"
set "FRONTEND_DIR=%PROJECT_DIR%\frontend"
set "BACKUP_DIR=D:\desktop\vanmoly-backup-v3.0.5"

:: Check backup directory
echo [1/5] Checking backup directory...
if not exist "%BACKUP_DIR%" (
    mkdir "%BACKUP_DIR%"
    echo      Created: %BACKUP_DIR%
) else (
    echo      Exists
)

echo.
echo [2/5] Backup current version...
xcopy /Y /I "%BACKEND_DIR%\*.py" "%BACKUP_DIR%\backend\" >nul 2>&1
xcopy /Y /I "%BACKEND_DIR%\app\*.py" "%BACKUP_DIR%\backend\app\" >nul 2>&1
xcopy /Y /I "%BACKEND_DIR%\app\models\*.py" "%BACKUP_DIR%\backend\app\models\" >nul 2>&1
xcopy /Y /I "%BACKEND_DIR%\app\routes\*.py" "%BACKUP_DIR%\backend\app\routes\" >nul 2>&1
echo      Backup complete

echo.
echo [3/5] Starting backend server...
cd /d "%BACKEND_DIR%"

:: Check if port 8080 is in use
netstat -ano | findstr ":8080" >nul
if %errorlevel% equ 0 (
    echo      Port 8080 is in use, killing existing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

:: Start backend in new window
start "Backend-V3.0.5" cmd /c "python run_waitress.py"

:: Wait for backend to start
echo      Waiting for backend to start...
set /a count=0
:check_backend
set /a count+=1
timeout /t 1 /nobreak >nul
curl -s http://localhost:8080/api/v3/health >nul 2>&1
if %errorlevel% neq 0 (
    if %count% lss 10 goto check_backend
    echo      Backend start timeout, please check manually
) else (
    echo      Backend started (port: 8080)
)

echo.
echo [4/5] Starting frontend dev server...
cd /d "%FRONTEND_DIR%"

:: Check if port 5173 is in use
netstat -ano | findstr ":5173" >nul
if %errorlevel% equ 0 (
    echo      Port 5173 is in use, killing existing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

:: Start frontend in new window
start "Frontend-V3.0.5" cmd /c "npm run dev"

:: Wait for frontend to start
echo      Waiting for frontend to start...
set /a count=0
:check_frontend
set /a count+=1
timeout /t 1 /nobreak >nul
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% neq 0 (
    if %count% lss 15 goto check_frontend
    echo      Frontend start timeout, please check manually
) else (
    echo      Frontend started (port: 5173)
)

echo.
echo [5/5] Opening browser...
timeout /t 2 /nobreak >nul
start "" "http://localhost:5173"
echo      Browser opened

echo.
echo ==========================================
echo    V3.0.5 Startup Complete!
echo    Frontend: http://localhost:5173
echo    Admin: http://localhost:5173/admin
echo    API: http://localhost:8080
echo ==========================================
echo.
pause
