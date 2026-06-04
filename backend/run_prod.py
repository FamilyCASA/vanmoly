"""
D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 - 生产环境启动
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from config import config

# 使用生产配置
app = create_app(config['production'])

if __name__ == '__main__':
    # 关闭重载，避免SIGKILL
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
