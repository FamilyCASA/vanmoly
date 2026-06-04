"""
D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 - 生产环境启动脚本
使用waitress减少资源占用
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 禁用SQLAlchemy日志
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

from app import create_app
from config import config

app = create_app(config['production'])

if __name__ == '__main__':
    from waitress import serve
    print("=" * 50)
    print("D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 - 生产模式")
    print("=" * 50)
    print("服务地址: http://0.0.0.0:8080")
    print("API前缀: /api/v3/")
    print("=" * 50)
    
    # 使用waitress生产服务器，单线程减少资源占用
    serve(app, host='0.0.0.0', port=8080, threads=2, channel_timeout=30)
