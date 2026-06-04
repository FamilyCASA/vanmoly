#!/usr/bin/env python3
"""启动后端 - 绕过 shell 路径截断问题"""
import os
import sys
import subprocess

PROJECT = "/Users/mac/Desktop/VANMOLY-SYS-V3.0"
BACKEND_DIR = os.path.join(PROJECT, "backend")
LOG_FILE = os.path.join(PROJECT, "logs", "backend.log")

os.chdir(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)

# 启动 Flask
from app import app
print(f"[OK] 后端启动于 http://0.0.0.0:8080")
print(f"[日志] {LOG_FILE}")
sys.stdout.flush()

app.run(host="0.0.0.0", port=8080, debug=False)
