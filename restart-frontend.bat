@echo off
chcp 65001 >nul
title 重启前端服务
color 0E

echo ==========================================
echo    重启前端服务
echo ==========================================
echo.

set "FRONTEND_DIR=D:\desktop\VANMOLY-SYS-V3.0\frontend"

echo [1/2] 停止现有Node进程...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul
echo      已停止

echo.
echo [2/2] 重新启动前端服务...
cd /d "%FRONTEND_DIR%"
start "梵木里前端 - V3.0.5" cmd /k "npm run dev"
timeout /t 5 /nobreak >nul
echo      前端服务已启动

echo.
echo ==========================================
echo    重启完成！
echo    请刷新浏览器或重新访问 http://localhost:3000/book
echo ==========================================
pause
