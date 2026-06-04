# -*- coding: utf-8 -*-
from app import create_app
from config import config
import os

env = os.environ.get('FLASK_ENV', 'production')
app = create_app(config[env])

if __name__ == '__main__':
    from waitress import serve
    print('[启动] waitress 0.0.0.0:8080')
    serve(app, host='0.0.0.0', port=8080, threads=4)
