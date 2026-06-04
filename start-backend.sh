#!/bin/bash
# 启动后端 - 用 Python 脚本绕过 shell 路径截断问题

PROJECT_DIR="/Users/mac/Desktop/VANMOLY-SYS-V3.0"
LOG_FILE="$PROJECT_DIR/logs/backend.log"

mkdir -p "$PROJECT_DIR/logs"

cd "$PROJECT_DIR/backend" || exit 1

echo "[$(date)] 启动后端..." >> "$LOG_FILE"

# 用 python -c 方式启动，避免 shell 路径解析问题
nohup python3 -c "
import sys, os
os.chdir('$PROJECT_DIR/backend')
sys.path.insert(0, '$PROJECT_DIR/backend')
from app import app
app.run(host='0.0.0.0', port=8080, debug=False)
" >> "$LOG_FILE" 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > "$PROJECT_DIR/backend.pid"

echo "后端启动中，PID: $BACKEND_PID"
echo "日志: $LOG_FILE"

# 等待后端启动
sleep 3
if curl -s --max-time 5 http://localhost:8080/api/v3/health > /dev/null 2>&1; then
    echo "✅ 后端启动成功: http://localhost:8080"
else
    echo "⚠️  后端可能还在启动中，请检查日志"
fi
