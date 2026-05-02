# -*- coding: utf-8 -*-
"""
分店管理路由
权限：仅超级管理员可访问
功能：管理分店信息、独立数据库
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os
import shutil

from app import db
from app.models.auth_v2 import Store, UserV2
from app.routes.auth_routes_v2 import jwt_required_v2

store_bp = Blueprint('store', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({'code': code, 'message': message, 'data': data}), code


def check_super_admin(current_user):
    """检查是否为超级管理员"""
    if current_user.get('role') != 'super_admin':
        return False
    return True


@store_bp.route('/stores', methods=['GET'])
@jwt_required_v2
def get_stores(current_user):
    """
    获取分店列表
    权限：仅超级管理员
    """
    if not check_super_admin(current_user):
        return api_response(403, '权限不足，仅超级管理员可访问')
    
    try:
        # 查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status', '')
        keyword = request.args.get('keyword', '')
        
        # 构建查询
        query = Store.query
        
        if status:
            query = query.filter(Store.status == status)
        
        if keyword:
            query = query.filter(
                db.or_(
                    Store.name.contains(keyword),
                    Store.code.contains(keyword)
                )
            )
        
        # 排序和分页
        query = query.order_by(Store.created_at.desc())
        total = query.count()
        stores = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 补充店长信息
        data = []
        for store in stores:
            store_dict = store.to_dict()
            if store.manager_id:
                manager = UserV2.query.get(store.manager_id)
                if manager:
                    store_dict['manager_name'] = manager.nickname
            data.append(store_dict)
        
        return api_response(200, '获取成功', {
            'list': data,
            'total': total,
            'page': page,
            'page_size': page_size
        })
        
    except Exception as e:
        current_app.logger.error(f'获取分店列表失败: {str(e)}')
        return api_response(500, f'服务器错误: {str(e)}')


@store_bp.route('/stores', methods=['POST'])
@jwt_required_v2
def create_store(current_user):
    """
    创建新分店
    权限：仅超级管理员
    功能：
    1. 创建分店记录
    2. 初始化独立数据库
    """
    if not check_super_admin(current_user):
        return api_response(403, '权限不足，仅超级管理员可访问')
    
    try:
        data = request.get_json()
        
        # 必填字段
        code = data.get('code', '').strip()
        name = data.get('name', '').strip()
        
        if not code or not name:
            return api_response(400, '分店编码和名称不能为空')
        
        # 检查编码唯一性
        if Store.query.filter(Store.code == code).first():
            return api_response(400, f'分店编码 {code} 已存在')
        
        # 生成租户ID
        tenant_id = f"tenant_{code.lower()}"
        
        # 确定数据库路径
        instance_dir = os.path.join(current_app.config['BASE_DIR'], 'instance')
        db_filename = f"store_{code.lower()}.db"
        db_path = os.path.join(instance_dir, db_filename)
        
        # 创建分店记录
        store = Store(
            code=code,
            name=name,
            tenant_id=tenant_id,
            db_path=db_path,
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            manager_id=data.get('manager_id'),
            status=data.get('status', 'active'),
            province=data.get('province', ''),
            city=data.get('city', ''),
            district=data.get('district', ''),
            opening_date=data.get('opening_date'),
            business_hours=data.get('business_hours', ''),
            description=data.get('description', '')
        )
        
        db.session.add(store)
        db.session.commit()
        
        # 初始化独立数据库
        try:
            init_store_database(db_path, store.id)
            store.db_status = 'initialized'
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'初始化分店数据库失败: {str(e)}')
            store.db_status = 'failed'
            db.session.commit()
        
        return api_response(201, '分店创建成功', store.to_dict())
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'创建分店失败: {str(e)}')
        return api_response(500, f'服务器错误: {str(e)}')


@store_bp.route('/stores/<int:store_id>', methods=['GET'])
@jwt_required_v2
def get_store(current_user, store_id):
    """
    获取分店详情
    权限：仅超级管理员
    """
    if not check_super_admin(current_user):
        return api_response(403, '权限不足，仅超级管理员可访问')
    
    try:
        store = Store.query.get(store_id)
        if not store:
            return api_response(404, '分店不存在')
        
        store_dict = store.to_dict()
        
        # 补充店长信息
        if store.manager_id:
            manager = UserV2.query.get(store.manager_id)
            if manager:
                store_dict['manager_name'] = manager.nickname
                store_dict['manager_phone'] = manager.phone
        
        # 统计员工数
        employee_count = UserV2.query.filter(UserV2.store_id == store_id).count()
        store_dict['employee_count'] = employee_count
        
        return api_response(200, '获取成功', store_dict)
        
    except Exception as e:
        current_app.logger.error(f'获取分店详情失败: {str(e)}')
        return api_response(500, f'服务器错误: {str(e)}')


@store_bp.route('/stores/<int:store_id>', methods=['PUT'])
@jwt_required_v2
def update_store(current_user, store_id):
    """
    更新分店信息
    权限：仅超级管理员
    """
    if not check_super_admin(current_user):
        return api_response(403, '权限不足，仅超级管理员可访问')
    
    try:
        store = Store.query.get(store_id)
        if not store:
            return api_response(404, '分店不存在')
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            store.name = data['name'].strip()
        if 'address' in data:
            store.address = data['address']
        if 'phone' in data:
            store.phone = data['phone']
        if 'manager_id' in data:
            store.manager_id = data['manager_id']
        if 'status' in data:
            store.status = data['status']
        if 'province' in data:
            store.province = data['province']
        if 'city' in data:
            store.city = data['city']
        if 'district' in data:
            store.district = data['district']
        if 'opening_date' in data:
            store.opening_date = data['opening_date']
        if 'business_hours' in data:
            store.business_hours = data['business_hours']
        if 'description' in data:
            store.description = data['description']
        
        store.updated_at = datetime.now()
        db.session.commit()
        
        return api_response(200, '更新成功', store.to_dict())
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'更新分店失败: {str(e)}')
        return api_response(500, f'服务器错误: {str(e)}')


@store_bp.route('/stores/<int:store_id>', methods=['DELETE'])
@jwt_required_v2
def delete_store(current_user, store_id):
    """
    删除分店（软删除）
    权限：仅超级管理员
    注意：删除前需确认无关联数据
    """
    if not check_super_admin(current_user):
        return api_response(403, '权限不足，仅超级管理员可访问')
    
    try:
        store = Store.query.get(store_id)
        if not store:
            return api_response(404, '分店不存在')
        
        # 检查是否有关联员工
        employee_count = UserV2.query.filter(UserV2.store_id == store_id).count()
        if employee_count > 0:
            return api_response(400, f'该分店有 {employee_count} 名员工，无法删除')
        
        # 软删除
        store.status = 'deleted'
        store.updated_at = datetime.now()
        db.session.commit()
        
        return api_response(200, '删除成功')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'删除分店失败: {str(e)}')
        return api_response(500, f'服务器错误: {str(e)}')


@store_bp.route('/stores/options', methods=['GET'])
@jwt_required_v2
def get_store_options(current_user):
    """
    获取分店选项（用于下拉选择）
    权限：所有登录用户
    """
    try:
        stores = Store.query.filter(Store.status == 'active').all()
        data = [{'value': s.id, 'label': s.name} for s in stores]
        return api_response(200, '获取成功', data)
    except Exception as e:
        current_app.logger.error(f'获取分店选项失败: {str(e)}')
        return api_response(500, f'服务器错误: {str(e)}')


@store_bp.route('/stores/<int:store_id>/stats', methods=['GET'])
@jwt_required_v2
def get_store_stats(current_user, store_id):
    """
    获取分店统计数据
    权限：仅超级管理员
    """
    if not check_super_admin(current_user):
        return api_response(403, '权限不足，仅超级管理员可访问')
    
    try:
        store = Store.query.get(store_id)
        if not store:
            return api_response(404, '分店不存在')
        
        # 统计员工
        employee_count = UserV2.query.filter(UserV2.store_id == store_id).count()
        
        # 检查数据库状态
        db_status = '未初始化'
        db_size = 0
        if store.db_path and os.path.exists(store.db_path):
            db_status = '正常'
            db_size = os.path.getsize(store.db_path)
        
        return api_response(200, '获取成功', {
            'employee_count': employee_count,
            'db_status': db_status,
            'db_size': db_size,
            'db_size_mb': round(db_size / 1024 / 1024, 2)
        })
        
    except Exception as e:
        current_app.logger.error(f'获取分店统计失败: {str(e)}')
        return api_response(500, f'服务器错误: {str(e)}')


def init_store_database(db_path, store_id):
    """
    初始化分店独立数据库
    创建基础表结构
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 创建数据库连接
    engine = create_engine(f'sqlite:///{db_path}')
    
    # 创建基础表
    with engine.connect() as conn:
        # 创建基础表结构
        conn.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(32) NOT NULL,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                wechat VARCHAR(50),
                address TEXT,
                source VARCHAR(50),
                status VARCHAR(20) DEFAULT 'pending',
                assigned_to INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(32) NOT NULL,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                source VARCHAR(50),
                status VARCHAR(20) DEFAULT 'new',
                assigned_to INTEGER,
                score INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(32) NOT NULL,
                title VARCHAR(200) NOT NULL,
                style VARCHAR(50),
                area DECIMAL(10,2),
                budget DECIMAL(12,2),
                status VARCHAR(20) DEFAULT 'draft',
                customer_id INTEGER,
                designer_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(32) NOT NULL,
                quote_no VARCHAR(50),
                customer_id INTEGER,
                total_amount DECIMAL(12,2),
                status VARCHAR(20) DEFAULT 'draft',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(32) NOT NULL,
                contract_no VARCHAR(50),
                customer_id INTEGER,
                total_amount DECIMAL(12,2),
                status VARCHAR(20) DEFAULT 'pending',
                signed_at DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        conn.execute('CREATE INDEX IF NOT EXISTS idx_customers_tenant ON customers(tenant_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_leads_tenant ON leads(tenant_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_cases_tenant ON cases(tenant_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_quotes_tenant ON quotes(tenant_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_contracts_tenant ON contracts(tenant_id)')
        
        conn.commit()
    
    return True
