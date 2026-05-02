"""
认证工具函数
"""
from flask import request
from app.routes.auth_routes import verify_token, api_response


def jwt_required(f):
    """JWT 认证装饰器"""
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
        
        # 将用户信息存入 g
        from flask import g
        g.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated


def get_current_user():
    """获取当前登录用户"""
    from flask import g
    return getattr(g, 'current_user', None)


def get_current_user_id():
    """获取当前登录用户ID"""
    user = get_current_user()
    return user.get('id') if user else None


def admin_required(f):
    """管理员权限装饰器"""
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
        
        if payload.get('role') != 'admin':
            return api_response(code=403, message='需要管理员权限')
        
        from flask import g
        g.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated
