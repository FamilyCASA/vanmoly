"""后端启动脚本 V3.0 - 单一数据库版本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from waitress import serve
from app import create_app

app = create_app()
print('启动 waitress 服务：0.0.0.0:8080')
serve(app, host='0.0.0.0', port=8080, threads=4)
