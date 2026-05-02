"""
D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 - 保持活动启动脚本
使用主应用配置连接正确数据库
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 先设置环境变量
os.environ['SQLALCHEMY_ECHO'] = 'False'

from app import create_app
from config import config

app = create_app(config['development'])



# 根路由
@app.route('/api/v3/')
def api_root():
    return jsonify({'code': 200, 'data': {'prefix': '/api/v3', 'version': '3.0.8'}, 'message': 'API Running'})

# 健康检查
@app.route('/api/v3/health')
def health():
    return jsonify({'code': 200, 'data': {'status': 'ok'}, 'message': 'OK'})









if __name__ == '__main__':
    print("=" * 50)
    print("D&B 帝标|设记家全安落地服务系统 DEMO V.0.1 - 简化模式")
    print("=" * 50)
    print("服务地址: http://0.0.0.0:8080")
    print("API前缀: /api/v3/")
    print("=" * 50)
    
    # 使用单线程模式减少资源占用
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=False)
