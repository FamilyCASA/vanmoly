"""
用户认证模块路由
API端点: /api/v3/auth
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import jwt
from app import db
from app.models import Employee
from config import Config


auth_bp = Blueprint('auth', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


def generate_token(user_id, username):
    """生成 JWT Token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')


def verify_token(token):
    """验证 JWT Token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# 默认管理员账号
MOCK_USERS = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password': 'admin123',
        'name': '管理员',
        'role': 'admin',
        'avatar': None
    }
}


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求体:
    {
        "username": "admin",
        "password": "admin123"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return api_response(code=400, message='请求体不能为空')
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return api_response(code=400, message='用户名和密码不能为空')
        
        # 验证用户
        user = MOCK_USERS.get(username)
        
        if not user or user['password'] != password:
            return api_response(code=401, message='用户名或密码错误')
        
        # 生成 JWT Token
        token = generate_token(user['id'], user['username'])
        
        return api_response(data={
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'name': user['name'],
                'role': user['role'],
                'avatar': user['avatar']
            }
        })
        
    except Exception as e:
        return api_response(code=500, message=f'登录失败: {str(e)}')


@auth_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return api_response(code=401, message='未提供认证令牌')
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return api_response(code=401, message='令牌无效或已过期')
    
    user = MOCK_USERS.get(payload['username'])
    if not user:
        return api_response(code=401, message='用户不存在')
    
    return api_response(data={
        'id': user['id'],
        'username': user['username'],
        'name': user['name'],
        'role': user['role'],
        'avatar': user['avatar']
    })


@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    # JWT 无状态，客户端删除 token 即可
    return api_response(message='登出成功')


def token_required(f):
    """验证登录 token 的装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return api_response(code=401, message='未提供认证令牌')
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return api_response(code=401, message='令牌无效或已过期')
        
        user = MOCK_USERS.get(payload['username'])
        if not user:
            return api_response(code=401, message='用户不存在')
        
        return f(user, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """验证管理员权限的装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return api_response(code=401, message='未提供认证令牌')
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return api_response(code=401, message='令牌无效或已过期')
        
        user = MOCK_USERS.get(payload['username'])
        if not user:
            return api_response(code=401, message='用户不存在')
        
        if user.get('role') != 'admin':
            return api_response(code=403, message='需要管理员权限')
        
        return f(user, *args, **kwargs)
    
    return decorated
