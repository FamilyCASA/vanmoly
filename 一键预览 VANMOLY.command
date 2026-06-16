#!/bin/bash
# ============================================
# 🚀 VANMOLY 帝标·设记家全案服务系统 — 一键预览
# 双击即可启动所有服务并自动打开浏览器
# 按 Enter 键停止服务并关闭窗口
# ============================================

PROJECT_DIR="/Users/mac/VANMOLY-SYS"
LOGS_DIR="$PROJECT_DIR/logs"
BACKEND_LOG="$LOGS_DIR/backend.log"
FRONTEND_LOG="$LOGS_DIR/frontend.log"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ 错误：找不到项目目录${NC}"
    echo "   路径: $PROJECT_DIR"
    echo "   请检查项目是否已正确安装。"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

# 清屏
clear
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║   🚀  VANMOLY  帝标·设记家  全案服务系统 V3.4          ║"
echo "║               ───  一键预览  ───                       ║"
echo "║                                                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 创建日志目录
mkdir -p "$LOGS_DIR"

# 清理旧进程
echo -e "${YELLOW}⏹️  清理旧进程...${NC}"
lsof -ti:8080 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:5173 2>/dev/null | xargs kill -9 2>/dev/null
sleep 1
echo -e "${GREEN}   已清理端口 8080 和 5173${NC}"
echo ""

# ── 启动后端 ──
echo -e "${YELLOW}⚙️  启动后端服务 (Flask :8080)...${NC}"
cd "$PROJECT_DIR/backend"
nohup python3 run.py > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$PROJECT_DIR/.backend.pid"

for i in $(seq 1 30); do
    if curl -s http://localhost:8080 >/dev/null 2>&1; then
        echo -e "${GREEN}   ✅ 后端已就绪 (PID: $BACKEND_PID)${NC}"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo -e "${RED}   ⚠️  后端启动超时，请查看日志:${NC}"
        echo -e "${YELLOW}       tail -f $BACKEND_LOG${NC}"
    fi
    sleep 1
done
echo ""

# ── 启动前端 ──
echo -e "${YELLOW}⚙️  启动前端服务 (Vite :5173)...${NC}"
cd "$PROJECT_DIR/frontend"
nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$PROJECT_DIR/.frontend.pid"

for i in $(seq 1 30); do
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        echo -e "${GREEN}   ✅ 前端已就绪 (PID: $FRONTEND_PID)${NC}"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo -e "${RED}   ⚠️  前端启动超时，请查看日志:${NC}"
        echo -e "${YELLOW}       tail -f $FRONTEND_LOG${NC}"
    fi
    sleep 1
done
echo ""

# ── 打开浏览器 ──
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   ✅  系统启动完成！                                    ║"
echo "║                                                        ║"
echo "║   📱 前端界面:  http://localhost:5173                   ║"
echo "║   🔗 后端 API:  http://localhost:8080                   ║"
echo "║                                                        ║"
echo "║   👤 超管账号:  vanmoly / Van9999                       ║"
echo "║   👤 测试账号:  test    / van654321                     ║"
echo "║                                                        ║"
echo "║   📋 后端日志:  $BACKEND_LOG           ║"
echo "║   📋 前端日志:  $FRONTEND_LOG          ║"
echo "║                                                        ║"
echo "║   🛑 按 Enter 键 = 停止所有服务并关闭窗口              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 打开浏览器
open "http://localhost:5173" 2>/dev/null

echo -e "${YELLOW}💡 按 Enter 键可随时停止服务...${NC}"
read -r

# ── 停止服务 ──
echo ""
echo -e "${YELLOW}⏹️  正在停止服务...${NC}"
lsof -ti:8080 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:5173 2>/dev/null | xargs kill -9 2>/dev/null
rm -f "$PROJECT_DIR/.backend.pid" "$PROJECT_DIR/.frontend.pid"
echo -e "${GREEN}✅ 服务已全部停止。${NC}"
sleep 1
exit 0
