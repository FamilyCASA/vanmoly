#!/bin/bash
# ============================================
# 帝标·设记家全案落地服务系统 V3.4.0
# 一键启动脚本 (Mac OS 版本)
# 替代 Windows 的 start-all-v3.0.5.bat
# ============================================

echo "=========================================="
echo "  帝标·设记家全案服务系统 V3.4.0"
echo "  正在启动..."
echo "=========================================="
echo ""

# 项目路径
PROJECT_DIR="/Users/mac/VANMOLY-SYS"
cd "$PROJECT_DIR" || exit 1

# 检查依赖
echo "[1/5] 检查运行环境..."
if ! command -v python3 &>/dev/null; then
    echo "❌ 错误: 未安装 Python 3.11+"
    echo "   请先运行: brew install python3"
    exit 1
fi

if ! command -v node &>/dev/null; then
    echo "❌ 错误: 未安装 Node.js 18+"
    echo "   请先运行: brew install node"
    exit 1
fi

echo "✅ Python $(python3 --version 2>&1 | awk '{print $2}')"
echo "✅ Node.js $(node --version)"
echo ""

# 创建日志目录
echo "[2/5] 准备日志目录..."
mkdir -p "$PROJECT_DIR/logs"
echo "   日志目录: $PROJECT_DIR/logs"
echo ""

# 停止旧进程
echo "[3/5] 停止旧进程..."
lsof -ti:8080 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 2
echo "   已清理端口 8080 和 5173"
echo ""

# 启动后端
echo "[4/5] 启动后端服务 (Flask + Waitress)..."
cd "$PROJECT_DIR/backend" || exit 1

# 检查 Python 依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "   ⚠️  Python 依赖缺失，正在安装..."
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

# 启动后端 (后台运行)
nohup python3 run.py > "$PROJECT_DIR/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo "   后端进程 PID: $BACKEND_PID"
echo "   $BACKEND_PID" > "$PROJECT_DIR/.backend.pid"

# 等待后端启动
echo "   等待后端启动..."
for i in {1..20}; do
    if curl -s http://localhost:8080/api >/dev/null 2>&1; then
        echo "   ✅ 后端启动成功: http://localhost:8080"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "   ❌ 后端启动超时"
        echo "   请查看日志: tail -f $PROJECT_DIR/logs/backend.log"
        exit 1
    fi
    sleep 1
done
echo ""

# 启动前端
echo "[5/5] 启动前端服务 (Vite + Vue 3)..."
cd "$PROJECT_DIR/frontend" || exit 1

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "   ⚠️  前端依赖缺失，正在安装..."
    npm install
fi

# 启动前端 (后台运行)
nohup npm run dev > "$PROJECT_DIR/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "   前端进程 PID: $FRONTEND_PID"
echo "   $FRONTEND_PID" > "$PROJECT_DIR/.frontend.pid"

# 等待前端启动
echo "   等待前端启动..."
for i in {1..20}; do
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        echo "   ✅ 前端启动成功: http://localhost:5173"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "   ❌ 前端启动超时"
        echo "   请查看日志: tail -f $PROJECT_DIR/logs/frontend.log"
        exit 1
    fi
    sleep 1
done
echo ""

# 完成
echo "=========================================="
echo "  ✅ 系统启动完成！"
echo "=========================================="
echo ""
echo "📱 访问地址:"
echo "   前端界面: http://localhost:5173"
echo "   后端 API: http://localhost:8080"
echo ""
echo "📋 日志查看:"
echo "   后端日志: tail -f $PROJECT_DIR/logs/backend.log"
echo "   前端日志: tail -f $PROJECT_DIR/logs/frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   运行: bash $PROJECT_DIR/stop-system.sh"
echo ""
echo "🌐 正在打开浏览器..."
sleep 2
open http://localhost:5173

exit 0
