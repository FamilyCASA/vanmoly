"""
D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 启动入口
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from config import config

# 获取环境配置
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(config[env])

if __name__ == '__main__':
    # 生产服务器（waitress）
    from waitress import serve
    print('[启动] 后端服务 waitress → http://0.0.0.0:8080')
    serve(app, host='0.0.0.0', port=8080, threads=4)
