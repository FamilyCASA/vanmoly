@echo off
chcp 65001 >nul
title 梵木里系统 - 回退到 V3.0.5
color 0C

echo ==========================================
echo    梵木里全案服务系统
echo    回退到 V3.0.5 版本
echo ==========================================
echo.

set "PROJECT_DIR=D:\desktop\VANMOLY-SYS-V3.0"
set "BACKEND_DIR=%PROJECT_DIR%\backend"
set "FRONTEND_DIR=%PROJECT_DIR%\frontend"
set "BACKUP_DIR=D:\desktop\vanmoly-backup-v3.0.5"

:: 检查备份是否存在
if not exist "%BACKUP_DIR%" (
    echo [错误] 备份目录不存在: %BACKUP_DIR%
    echo        无法回退版本。
    pause
    exit /b 1
)

echo [1/3] 停止相关服务...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul
echo      服务已停止

echo.
echo [2/3] 恢复备份文件...
xcopy /Y /I "%BACKUP_DIR%\backend\*.py" "%BACKEND_DIR%\" >nul 2>&1
xcopy /Y /I "%BACKUP_DIR%\backend\app\*.py" "%BACKEND_DIR%\app\" >nul 2>&1
xcopy /Y /I "%BACKUP_DIR%\backend\app\models\*.py" "%BACKEND_DIR%\app\models\" >nul 2>&1
xcopy /Y /I "%BACKUP_DIR%\backend\app\routes\*.py" "%BACKEND_DIR%\app\routes\" >nul 2>&1
xcopy /Y /I "%BACKUP_DIR%\frontend\views\*.vue" "%FRONTEND_DIR%\src\views\" >nul 2>&1
xcopy /Y /I "%BACKUP_DIR%\frontend\components\*.vue" "%FRONTEND_DIR%\src\components\" >nul 2>&1
echo      文件恢复完成

echo.
echo [3/3] 版本回退完成！
echo.
echo ==========================================
echo    已回退到 V3.0.5 版本
echo    请重新运行 start-all-v3.0.5.bat 启动系统
echo ==========================================
echo.
pause
