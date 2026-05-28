# -*- coding: utf-8 -*-
"""
商学院知识库模块 - API路由
VANMOLY-SYS V3.2
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from app import db
from app.models.knowledge import KnowledgeBase, KnowledgeNode, KnowledgeShare, FrontUser
from app.routes.auth_routes_v2 import jwt_required_v2

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/v3/knowledge')


# ============================================================================
# 工具函数
# ============================================================================

def make_token():
    return secrets.token_hex(16)


def hash_pwd(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def parse_bool(val):
    if isinstance(val, bool):
        return val
    if str(val).lower() in ('true', '1', 'yes'):
        return True
    return False


# ============================================================================
# 知识库管理 API（后台）
# ============================================================================

@knowledge_bp.route('/bases', methods=['GET'])
def get_bases():
    """获取知识库列表"""
    status = request.args.get('status', type=int)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)

    q = KnowledgeBase.query
    if status is not None:
        q = q.filter_by(status=status)

    q = q.order_by(KnowledgeBase.sort_order.asc(), KnowledgeBase.id.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'items': [b.to_dict() for b in items],
            'total': total,
            'page': page,
            'pages': (total + page_size - 1) // page_size
        }
    })


@knowledge_bp.route('/bases', methods=['POST'])
@jwt_required_v2
def create_base(current_user_id):
    """创建知识库"""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'code': 400, 'message': '知识库名称不能为空'}), 400

    base = KnowledgeBase(
        name=name,
        description=data.get('description', ''),
        cover_image=data.get('cover_image', ''),
        related_module=data.get('related_module', ''),
        status=data.get('status', 1),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(base)
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': base.to_dict()})


@knowledge_bp.route('/bases/<int:base_id>', methods=['GET'])
def get_base(base_id):
    """获取知识库详情"""
    base = KnowledgeBase.query.get_or_404(base_id)
    return jsonify({'code': 200, 'message': 'success', 'data': base.to_dict()})


@knowledge_bp.route('/bases/<int:base_id>', methods=['PUT'])
@jwt_required_v2
def update_base(current_user_id, base_id):
    """更新知识库"""
    base = KnowledgeBase.query.get_or_404(base_id)
    data = request.get_json() or {}
    for field in ['name', 'description', 'cover_image', 'related_module', 'status', 'sort_order']:
        if field in data:
            setattr(base, field, data[field])
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': base.to_dict()})


@knowledge_bp.route('/bases/<int:base_id>', methods=['DELETE'])
@jwt_required_v2
def delete_base(current_user_id, base_id):
    """删除知识库（连带节点）"""
    base = KnowledgeBase.query.get_or_404(base_id)
    db.session.delete(base)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'})


@knowledge_bp.route('/bases/<int:base_id>/tree', methods=['GET'])
def get_base_tree(base_id):
    """获取知识库树状结构"""
    base = KnowledgeBase.query.get_or_404(base_id)
    root_nodes = base.nodes.filter_by(parent_id=0).order_by(KnowledgeNode.sort_order.asc()).all()
    tree = [n.to_dict(include_children=True, include_content=True) for n in root_nodes]
    return jsonify({'code': 200, 'message': 'success', 'data': tree})


# ============================================================================
# 节点管理 API（后台）
# ============================================================================

@knowledge_bp.route('/nodes', methods=['POST'])
@jwt_required_v2
def create_node(current_user_id):
    """新增节点"""
    data = request.get_json() or {}
    base_id = data.get('base_id')
    parent_id = data.get('parent_id', 0)
    node_name = data.get('node_name', '').strip()

    if not base_id:
        return jsonify({'code': 400, 'message': 'base_id不能为空'}), 400
    if not node_name:
        return jsonify({'code': 400, 'message': '节点名称不能为空'}), 400

    # 层级校验
    level = 1
    if parent_id > 0:
        parent = KnowledgeNode.query.get(parent_id)
        if not parent:
            return jsonify({'code': 404, 'message': '父节点不存在'}), 404
        level = parent.level + 1
        if level > 3:
            return jsonify({'code': 400, 'message': '最多支持三层分级，第四层仅支持文案'}), 400

    node = KnowledgeNode(
        base_id=base_id,
        parent_id=parent_id,
        node_name=node_name,
        level=level,
        sort_order=data.get('sort_order', 0),
        status=data.get('status', 1),
        content=data.get('content', ''),
        video_url=data.get('video_url', ''),
        file_ids=data.get('file_ids', []),
    )
    db.session.add(node)
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': node.to_dict(include_content=True)})


@knowledge_bp.route('/nodes/<int:node_id>', methods=['PUT'])
@jwt_required_v2
def update_node(current_user_id, node_id):
    """更新节点"""
    node = KnowledgeNode.query.get_or_404(node_id)
    data = request.get_json() or {}

    # 禁止升级层级
    if 'level' in data and data['level'] < node.level:
        return jsonify({'code': 400, 'message': '不允许降级节点层级'}), 400

    for field in ['node_name', 'level', 'sort_order', 'status', 'video_url', 'file_ids']:
        if field in data:
            setattr(node, field, data[field])
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': node.to_dict(include_content=True)})


@knowledge_bp.route('/nodes/<int:node_id>/content', methods=['PUT'])
@jwt_required_v2
def update_node_content(current_user_id, node_id):
    """更新节点文案内容"""
    node = KnowledgeNode.query.get_or_404(node_id)
    data = request.get_json() or {}
    node.content = data.get('content', '')
    if 'file_ids' in data:
        node.file_ids = data['file_ids']
    db.session.commit()
    return jsonify({'code': 200, 'message': '保存成功', 'data': node.to_dict(include_content=True)})


@knowledge_bp.route('/nodes/<int:node_id>', methods=['DELETE'])
@jwt_required_v2
def delete_node(current_user_id, node_id):
    """删除节点（连带子节点）"""
    def delete_cascade(node_id):
        children = KnowledgeNode.query.filter_by(parent_id=node_id).all()
        for child in children:
            delete_cascade(child.id)
        KnowledgeNode.query.filter_by(id=node_id).delete()

    node = KnowledgeNode.query.get_or_404(node_id)
    delete_cascade(node_id)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'})


@knowledge_bp.route('/nodes/<int:node_id>/view', methods=['POST'])
def increment_view(node_id):
    """增加节点浏览次数"""
    node = KnowledgeNode.query.get_or_404(node_id)
    node.view_count = (node.view_count or 0) + 1
    db.session.commit()
    return jsonify({'code': 200, 'message': 'success', 'data': {'view_count': node.view_count}})


# ============================================================================
# 公开 API（前台）
# ============================================================================

@knowledge_bp.route('/public/bases', methods=['GET'])
def public_bases():
    """前台获取知识库列表（仅展示状态）"""
    items = KnowledgeBase.query.filter_by(status=1).order_by(
        KnowledgeBase.sort_order.asc(), KnowledgeBase.id.asc()
    ).all()
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': [b.to_dict() for b in items]
    })


@knowledge_bp.route('/public/bases/<int:base_id>/tree', methods=['GET'])
def public_tree(base_id):
    """前台获取知识库树（仅展示节点）"""
    base = KnowledgeBase.query.get_or_404(base_id)
    if base.status != 1:
        return jsonify({'code': 403, 'message': '该知识库已停用'}), 403

    root_nodes = base.nodes.filter_by(parent_id=0, status=1).order_by(
        KnowledgeNode.sort_order.asc()
    ).all()
    tree = [n.to_dict(include_children=True, include_content=True) for n in root_nodes]
    return jsonify({'code': 200, 'message': 'success', 'data': tree})


# ============================================================================
# 分享功能
# ============================================================================

@knowledge_bp.route('/share', methods=['POST'])
@jwt_required_v2
def create_share(current_user_id):
    """生成分享链接"""
    data = request.get_json() or {}
    node_id = data.get('node_id')
    valid_days = data.get('valid_days', 30)

    node = KnowledgeNode.query.get_or_404(node_id)
    token = make_token()
    share = KnowledgeShare(
        node_id=node_id,
        employee_id=current_user_id,
        share_token=token,
        valid_days=valid_days,
        expire_at=datetime.utcnow() + timedelta(days=valid_days),
    )
    db.session.add(share)
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': share.to_dict()})


@knowledge_bp.route('/share/<token>', methods=['GET'])
def get_share(token):
    """通过Token获取分享内容"""
    share = KnowledgeShare.query.filter_by(share_token=token).first_or_404()
    if datetime.utcnow() > share.expire_at:
        return jsonify({'code': 403, 'message': '分享链接已过期'}), 403
    node = KnowledgeNode.query.get(share.node_id)
    if not node or node.status != 1:
        return jsonify({'code': 404, 'message': '该内容已下架'}), 404
    share.view_count += 1
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'node': node.to_dict(include_content=True),
            'share': share.to_dict()
        }
    })


@knowledge_bp.route('/shares', methods=['GET'])
@jwt_required_v2
def list_shares(current_user_id):
    """我的分享记录"""
    shares = KnowledgeShare.query.filter_by(employee_id=current_user_id).order_by(
        KnowledgeShare.created_at.desc()
    ).all()
    return jsonify({'code': 200, 'message': 'success', 'data': [s.to_dict() for s in shares]})


# ============================================================================
# 前台用户认证（简化版）
# ============================================================================

@knowledge_bp.route('/auth/register', methods=['POST'])
def register():
    """前台用户注册"""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')

    if not name or not phone or not password:
        return jsonify({'code': 400, 'message': '姓名、手机号、密码均不能为空'}), 400

    if FrontUser.query.filter_by(phone=phone).first():
        return jsonify({'code': 409, 'message': '该手机号已注册'}), 409

    user = FrontUser(
        name=name,
        phone=phone,
        region=data.get('region', ''),
        intention=data.get('intention', ''),
        password_hash=hash_pwd(password),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'code': 200, 'message': '注册成功', 'data': user.to_dict()})


@knowledge_bp.route('/auth/login', methods=['POST'])
def front_login():
    """前台用户登录"""
    data = request.get_json() or {}
    phone = data.get('phone', '').strip()
    password = data.get('password', '')

    user = FrontUser.query.filter_by(phone=phone).first()
    if not user or user.password_hash != hash_pwd(password):
        return jsonify({'code': 401, 'message': '手机号或密码错误'}), 401

    token = make_token()
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'token': token,
            'user': user.to_dict()
        }
    })


@knowledge_bp.route('/users/me', methods=['GET'])
def get_me():
    """获取当前用户（通过header token）"""
    token = request.headers.get('X-Front-Token', '')
    if not token:
        return jsonify({'code': 401, 'message': '请先登录'}), 401
    # 简化：token 即 make_token()，这里用 phone+固定密钥做简单校验
    # 实际生产应使用 JWT 或会话
    # 临时方案：从 Authorization: Bearer <front_token> 读取
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        phone = auth[7:]
        user = FrontUser.query.filter_by(phone=phone).first()
        if user:
            return jsonify({'code': 200, 'message': 'success', 'data': user.to_dict()})
    return jsonify({'code': 401, 'message': 'Token无效'}), 401


@knowledge_bp.route('/users/me', methods=['PUT'])
def update_me():
    """更新当前用户信息"""
    token = request.headers.get('X-Front-Token', '')
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({'code': 401, 'message': '请先登录'}), 401
    phone = auth[7:]
    user = FrontUser.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'code': 401, 'message': '用户不存在'}), 401

    data = request.get_json() or {}
    for field in ['name', 'region', 'intention']:
        if field in data:
            setattr(user, field, data[field])
    if 'password' in data and data['password']:
        user.password_hash = hash_pwd(data['password'])
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': user.to_dict()})
