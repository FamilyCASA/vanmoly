"""
D&B 帝标|设记家全案落地服务系统 DEMO V.0.1 - 端口8000启动
避免端口冲突
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

os.environ['SQLALCHEMY_ECHO'] = 'False'

from app import create_app
from config import config

app = create_app(config['development'])

if __name__ == '__main__':
    print("=" * 50)
    print("D&B 帝标|设记家全案落地服务系统 DEMO V.0.1")
    print("=" * 50)
    print("服务地址: http://0.0.0.0:8000")
    print("API前缀: /api/v3/")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
