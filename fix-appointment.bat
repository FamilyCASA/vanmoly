@echo off
chcp 65001 >nul
title 修复预约页面
color 0B

echo ==========================================
echo    修复预约页面
echo ==========================================
echo.

set "PROJECT_DIR=D:\desktop\VANMOLY-SYS-V3.0"
set "FRONTEND_DIR=%PROJECT_DIR%\frontend"

echo [1/4] 停止现有Node进程...
taskkill /F /IM node.exe 2>nul
taskkill /F /IM cmd.exe /FI "WINDOWTITLE eq *vite*" 2>nul
timeout /t 2 /nobreak >nul
echo      已停止

echo.
echo [2/4] 清除Vite缓存...
cd /d "%FRONTEND_DIR%"
if exist "node_modules\.vite" rmdir /S /Q "node_modules\.vite"
echo      缓存已清除

echo.
echo [3/4] 重新启动前端服务...
start "梵木里前端 - V3.0.5" cmd /k "npm run dev"
timeout /t 5 /nobreak >nul
echo      前端服务已启动

echo.
echo [4/4] 打开预约页面...
timeout /t 3 /nobreak >nul
start "" "http://localhost:3000/book"
echo      浏览器已打开

echo.
echo ==========================================
echo    修复完成！
echo    如果仍有问题，请检查浏览器控制台报错
echo ==========================================
pause
