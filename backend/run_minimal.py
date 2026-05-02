"""
D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 - 最小化启动脚本
减少内存占用，避免SIGKILL
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 设置环境变量减少日志输出
os.environ['SQLALCHEMY_ECHO'] = 'False'
os.environ['LOG_LEVEL'] = 'WARNING'

from flask import Flask
from config import Config

# 最小化Flask应用
app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_ECHO'] = False

# 只初始化数据库
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# 只注册必要的路由
@app.route('/api/v3/health')
def health():
    return {'status': 'ok', 'version': '3.0.8-minimal'}

@app.route('/api/v3/materials/skus')
def list_skus():
    from app.models.material_sku import MaterialSKU
    skus = MaterialSKU.query.filter_by(status='active', is_deleted=False).limit(50).all()
    return {
        'items': [s.to_dict() for s in skus],
        'total': MaterialSKU.query.count()
    }

@app.route('/api/v3/materials/categories')
def list_categories():
    from app.models.material_sku import MaterialCategory
    cats = MaterialCategory.query.filter_by(is_deleted=False).all()
    return {'items': [c.to_dict() for c in cats]}

if __name__ == '__main__':
    print("=" * 50)
    print("D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 - 最小化模式")
    print("=" * 50)
    print("服务地址: http://0.0.0.0:8080")
    print("API前缀: /api/v3/")
    print("=" * 50)
    
    # 使用单线程减少内存占用
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=False)
