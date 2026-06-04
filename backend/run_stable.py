"""
D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 - 稳定启动脚本
使用waitress生产服务器
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 禁用SQLAlchemy日志减少输出
os.environ['SQLALCHEMY_ECHO'] = 'False'

from app import create_app
from config import config

app = create_app(config['development'])

if __name__ == '__main__':
    print("=" * 50)
    print("D&B 帝标|设记家全案落地服务系统 DEMO V.0.1")
    print("=" * 50)
    
    try:
        from waitress import serve
        print("使用waitress生产服务器")
        print("服务地址: http://0.0.0.0:8080")
        print("API前缀: /api/v3/")
        print("=" * 50)
        serve(app, host='0.0.0.0', port=8080, threads=2)
    except ImportError:
        print("waitress未安装，使用Flask开发服务器")
        print("服务地址: http://0.0.0.0:8080")
        print("API前缀: /api/v3/")
        print("=" * 50)
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
