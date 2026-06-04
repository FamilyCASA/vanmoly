#!/bin/bash
# ============================================
# 帝标·设记家全案落地服务系统 V3.4.0
# 一键停止脚本 (Mac OS 版本)
# ============================================

echo "=========================================="
echo "  停止系统服务"
echo "=========================================="
echo ""

PROJECT_DIR="/Users/mac/VANMOLY-SYS"

# 停止后端
echo "[1/3] 停止后端服务..."
if [ -f "$PROJECT_DIR/.backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_DIR/.backend.pid")
    if ps -p "$BACKEND_PID" >/dev/null 2>&1; then
        echo "   停止后端进程 (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null
        sleep 1
    fi
    rm -f "$PROJECT_DIR/.backend.pid"
fi

# 强制清理端口 8080
if lsof -ti:8080 >/dev/null 2>&1; then
    echo "   清理端口 8080..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null
fi
echo "   ✅ 后端已停止"
echo ""

# 停止前端
echo "[2/3] 停止前端服务..."
if [ -f "$PROJECT_DIR/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_DIR/.frontend.pid")
    if ps -p "$FRONTEND_PID" >/dev/null 2>&1; then
        echo "   停止前端进程 (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null
        sleep 1
    fi
    rm -f "$PROJECT_DIR/.frontend.pid"
fi

# 强制清理端口 5173
if lsof -ti:5173 >/dev/null 2>&1; then
    echo "   清理端口 5173..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null
fi
echo "   ✅ 前端已停止"
echo ""

# 完成
echo "[3/3] 清理完成！"
echo "=========================================="
echo "  ✅ 所有服务已停止"
echo "=========================================="
echo ""
echo "💡 提示:"
echo "   重新启动请运行: bash $PROJECT_DIR/start-system.sh"
echo ""

exit 0
