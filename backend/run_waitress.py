"""
D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 - Waitress生产服务器
更稳定，避免SIGKILL
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from waitress import serve
from app import create_app
from config import config

app = create_app(config['production'])

if __name__ == '__main__':
    print("=" * 50)
    print("D&B 帝标|设记家全安落地服务系统 DEMO V.0.1")
    print("Waitress 生产服务器")
    print("=" * 50)
    print("服务地址: http://0.0.0.0:8080")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    serve(app, host='0.0.0.0', port=8080, threads=4)
