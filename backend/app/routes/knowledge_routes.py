# -*- coding: utf-8 -*-
"""
商学院知识库模块 - API路由
VANMOLY-SYS V3.3 知识库全面升级
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from app import db
from app.models.knowledge import (
    KnowledgeBase, KnowledgeNode, KnowledgeArticle, KnowledgeCategory,
    KnowledgeShare, FrontUser
)
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
    """获取知识库列表（支持category筛选）"""
    status = request.args.get('status', type=int)
    category = request.args.get('category', type=str)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)

    q = KnowledgeBase.query
    if status is not None:
        q = q.filter_by(status=status)
    if category:
        q = q.filter_by(category=category)

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
def create_base(current_user):
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
        # V3.3 新增
        category=data.get('category', '通用'),
        icon=data.get('icon', 'Document'),
        color=data.get('color', '#409EFF'),
        tags=data.get('tags', []),
        author_id=current_user['id'],
        view_count=0,
        is_public=data.get('is_public', False),
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
def update_base(current_user, base_id):
    """更新知识库"""
    base = KnowledgeBase.query.get_or_404(base_id)
    data = request.get_json() or {}
    # 旧字段
    for field in ['name', 'description', 'cover_image', 'related_module', 'status', 'sort_order']:
        if field in data:
            setattr(base, field, data[field])
    # V3.3 新增字段
    for field in ['category', 'icon', 'color', 'tags', 'view_count', 'is_public']:
        if field in data:
            setattr(base, field, data[field])
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': base.to_dict()})


@knowledge_bp.route('/bases/<int:base_id>', methods=['DELETE'])
@jwt_required_v2
def delete_base(current_user, base_id):
    """删除知识库（连带节点和文章）"""
    base = KnowledgeBase.query.get_or_404(base_id)
    db.session.delete(base)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'})


@knowledge_bp.route('/bases/<int:base_id>/tree', methods=['GET'])
def get_base_tree(base_id):
    """获取知识库树状结构（包含文章数量）"""
    base = KnowledgeBase.query.get_or_404(base_id)
    root_nodes = base.nodes.filter_by(parent_id=0).order_by(KnowledgeNode.sort_order.asc()).all()
    tree = [n.to_dict(include_children=True, include_content=True, include_article_count=True) for n in root_nodes]
    return jsonify({'code': 200, 'message': 'success', 'data': tree})


# ============================================================================
# 分类管理 API（V3.3 新增）
# ============================================================================

@knowledge_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取分类树"""
    root_cats = KnowledgeCategory.query.filter_by(parent_id=0).order_by(
        KnowledgeCategory.sort_order.asc()
    ).all()
    tree = [c.to_dict(include_children=True) for c in root_cats]
    return jsonify({'code': 200, 'message': 'success', 'data': tree})


@knowledge_bp.route('/categories', methods=['POST'])
@jwt_required_v2
def create_category(current_user):
    """创建分类"""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'code': 400, 'message': '分类名称不能为空'}), 400

    parent_id = data.get('parent_id', 0)
    level = 1
    if parent_id > 0:
        parent = KnowledgeCategory.query.get(parent_id)
        if not parent:
            return jsonify({'code': 404, 'message': '父分类不存在'}), 404
        level = parent.level + 1

    cat = KnowledgeCategory(
        name=name,
        parent_id=parent_id,
        level=level,
        sort_order=data.get('sort_order', 0),
        icon=data.get('icon', ''),
        color=data.get('color', ''),
        description=data.get('description', ''),
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': cat.to_dict()})


@knowledge_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@jwt_required_v2
def update_category(current_user, cat_id):
    """更新分类"""
    cat = KnowledgeCategory.query.get_or_404(cat_id)
    data = request.get_json() or {}
    for field in ['name', 'sort_order', 'icon', 'color', 'description']:
        if field in data:
            setattr(cat, field, data[field])
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': cat.to_dict()})


@knowledge_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@jwt_required_v2
def delete_category(current_user, cat_id):
    """删除分类（连同子分类）"""
    def delete_cascade(cat_id):
        children = KnowledgeCategory.query.filter_by(parent_id=cat_id).all()
        for child in children:
            delete_cascade(child.id)
        KnowledgeCategory.query.filter_by(id=cat_id).delete()

    cat = KnowledgeCategory.query.get_or_404(cat_id)
    delete_cascade(cat_id)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'})


# ============================================================================
# 节点管理 API（后台）
# ============================================================================

@knowledge_bp.route('/nodes', methods=['POST'])
@jwt_required_v2
def create_node(current_user):
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
        # V3.3 新增
        summary=data.get('summary', ''),
        cover_image=data.get('cover_image', ''),
        tags=data.get('tags', []),
        author_id=current_user['id'],
        word_count=data.get('word_count', 0),
        is_featured=data.get('is_featured', False),
        sort_type=data.get('sort_type', 'manual'),
    )
    db.session.add(node)
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': node.to_dict(include_content=True)})


@knowledge_bp.route('/nodes/<int:node_id>', methods=['PUT'])
@jwt_required_v2
def update_node(current_user, node_id):
    """更新节点（支持新字段）"""
    node = KnowledgeNode.query.get_or_404(node_id)
    data = request.get_json() or {}

    # 禁止升级层级
    if 'level' in data and data['level'] < node.level:
        return jsonify({'code': 400, 'message': '不允许降级节点层级'}), 400

    # 旧字段
    for field in ['node_name', 'level', 'sort_order', 'status', 'video_url', 'file_ids']:
        if field in data:
            setattr(node, field, data[field])
    # V3.3 新增字段
    for field in ['summary', 'cover_image', 'tags', 'word_count', 'is_featured', 'sort_type']:
        if field in data:
            setattr(node, field, data[field])
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': node.to_dict(include_content=True)})


@knowledge_bp.route('/nodes/<int:node_id>/content', methods=['PUT'])
@jwt_required_v2
def update_node_content(current_user, node_id):
    """更新节点文案内容"""
    node = KnowledgeNode.query.get_or_404(node_id)
    data = request.get_json() or {}
    node.content = data.get('content', '')
    if 'file_ids' in data:
        node.file_ids = data['file_ids']
    # 自动统计字数
    if node.content:
        import re
        text = re.sub(r'<[^>]+>', '', node.content)
        node.word_count = len(text.strip())
    db.session.commit()
    return jsonify({'code': 200, 'message': '保存成功', 'data': node.to_dict(include_content=True)})


@knowledge_bp.route('/nodes/<int:node_id>', methods=['DELETE'])
@jwt_required_v2
def delete_node(current_user, node_id):
    """删除节点（连带子节点和文章）"""
    def delete_cascade(node_id):
        children = KnowledgeNode.query.filter_by(parent_id=node_id).all()
        for child in children:
            delete_cascade(child.id)
        # 文章会通过 CASCADE 自动删除
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
# 文章管理 API（V3.3 新增）
# ============================================================================

@knowledge_bp.route('/nodes/<int:node_id>/articles', methods=['GET'])
def get_node_articles(node_id):
    """获取节点下文章列表"""
    node = KnowledgeNode.query.get_or_404(node_id)
    status = request.args.get('status', type=int)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)

    q = KnowledgeArticle.query.filter_by(node_id=node_id)
    if status is not None:
        q = q.filter_by(status=status)
    q = q.order_by(KnowledgeArticle.sort_order.asc(), KnowledgeArticle.id.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'items': [a.to_dict() for a in items],
            'total': total,
            'page': page,
            'pages': (total + page_size - 1) // page_size
        }
    })


@knowledge_bp.route('/articles', methods=['GET'])
def list_articles():
    """文章列表（支持分页、筛选）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    node_id = request.args.get('node_id', type=int)
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '').strip()

    q = KnowledgeArticle.query
    if node_id:
        q = q.filter_by(node_id=node_id)
    if status is not None:
        q = q.filter_by(status=status)
    if keyword:
        q = q.filter(KnowledgeArticle.title.contains(keyword))

    q = q.order_by(KnowledgeArticle.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'items': [a.to_dict() for a in items],
            'total': total,
            'page': page,
            'pages': (total + page_size - 1) // page_size
        }
    })


@knowledge_bp.route('/articles', methods=['POST'])
@jwt_required_v2
def create_article(current_user):
    """创建文章"""
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    node_id = data.get('node_id')

    if not title:
        return jsonify({'code': 400, 'message': '文章标题不能为空'}), 400
    if not node_id:
        return jsonify({'code': 400, 'message': 'node_id不能为空'}), 400

    node = KnowledgeNode.query.get(node_id)
    if not node:
        return jsonify({'code': 404, 'message': '节点不存在'}), 404

    # 自动统计字数
    word_count = 0
    content = data.get('content', '')
    if content:
        import re
        text = re.sub(r'<[^>]+>', '', content)
        word_count = len(text.strip())

    article = KnowledgeArticle(
        node_id=node_id,
        title=title,
        content=content,
        summary=data.get('summary', ''),
        cover_image=data.get('cover_image', ''),
        video_url=data.get('video_url', ''),
        file_ids=data.get('file_ids', []),
        tags=data.get('tags', []),
        author_id=current_user['id'],
        status=data.get('status', 1),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(article)
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': article.to_dict(include_content=True)})


@knowledge_bp.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """获取文章详情"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    return jsonify({'code': 200, 'message': 'success', 'data': article.to_dict(include_content=True)})


@knowledge_bp.route('/articles/<int:article_id>', methods=['PUT'])
@jwt_required_v2
def update_article(current_user, article_id):
    """更新文章"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    data = request.get_json() or {}

    for field in ['title', 'content', 'summary', 'cover_image', 'video_url',
                   'file_ids', 'tags', 'status', 'sort_order']:
        if field in data:
            setattr(article, field, data[field])

    # 自动统计字数
    if 'content' in data:
        import re
        text = re.sub(r'<[^>]+>', '', data.get('content', ''))
        # word_count不在上面列表中，单独设置

    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': article.to_dict(include_content=True)})


@knowledge_bp.route('/articles/<int:article_id>', methods=['DELETE'])
@jwt_required_v2
def delete_article(current_user, article_id):
    """删除文章"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'})


@knowledge_bp.route('/articles/<int:article_id>/like', methods=['POST'])
def like_article(article_id):
    """点赞文章"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    article.like_count = (article.like_count or 0) + 1
    db.session.commit()
    return jsonify({'code': 200, 'message': 'success', 'data': {'like_count': article.like_count}})


@knowledge_bp.route('/articles/<int:article_id>/view', methods=['POST'])
def increment_article_view(article_id):
    """增加文章浏览次数"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    article.view_count = (article.view_count or 0) + 1
    db.session.commit()
    return jsonify({'code': 200, 'message': 'success', 'data': {'view_count': article.view_count}})


# ============================================================================
# 搜索 API（V3.3 新增）
# ============================================================================

@knowledge_bp.route('/search', methods=['GET'])
def search():
    """全局搜索知识库（文章和节点）"""
    q = request.args.get('q', '').strip()
    base_id = request.args.get('base_id', type=int)
    category = request.args.get('category', type=str)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)

    if not q:
        return jsonify({'code': 200, 'message': 'success', 'data': {'items': [], 'total': 0}})

    results = []

    # 搜索文章
    article_q = KnowledgeArticle.query.filter(
        db.or_(
            KnowledgeArticle.title.contains(q),
            KnowledgeArticle.summary.contains(q),
        )
    ).filter_by(status=1)

    if base_id:
        # 通过node关联到base
        article_q = article_q.join(KnowledgeNode).filter(KnowledgeNode.base_id == base_id)

    articles = article_q.order_by(KnowledgeArticle.created_at.desc()).limit(50).all()
    for a in articles:
        node = KnowledgeNode.query.get(a.node_id)
        results.append({
            'type': 'article',
            'id': a.id,
            'title': a.title,
            'summary': a.summary,
            'cover_image': a.cover_image,
            'node_id': a.node_id,
            'base_id': node.base_id if node else None,
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M') if a.created_at else '',
        })

    # 搜索节点
    node_q = KnowledgeNode.query.filter(
        db.or_(
            KnowledgeNode.node_name.contains(q),
            KnowledgeNode.summary.contains(q),
        )
    )
    if base_id:
        node_q = node_q.filter_by(base_id=base_id)
    if category:
        node_q = node_q.join(KnowledgeBase).filter(KnowledgeBase.category == category)

    nodes = node_q.order_by(KnowledgeNode.created_at.desc()).limit(50).all()
    for n in nodes:
        results.append({
            'type': 'node',
            'id': n.id,
            'title': n.node_name,
            'summary': n.summary,
            'cover_image': n.cover_image,
            'base_id': n.base_id,
            'level': n.level,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M') if n.created_at else '',
        })

    # 分页
    total = len(results)
    start = (page - 1) * page_size
    end = start + page_size
    page_results = results[start:end]

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'items': page_results,
            'total': total,
            'page': page,
            'pages': (total + page_size - 1) // page_size
        }
    })


# ============================================================================
# 公开 API（前台）
# ============================================================================

@knowledge_bp.route('/public/bases', methods=['GET'])
def public_bases():
    """前台获取知识库列表（仅展示状态）"""
    category = request.args.get('category', type=str)
    q = KnowledgeBase.query.filter_by(status=1)
    if category:
        q = q.filter_by(category=category)
    items = q.order_by(
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
    tree = [n.to_dict(include_children=True, include_content=True, include_article_count=True) for n in root_nodes]
    return jsonify({'code': 200, 'message': 'success', 'data': tree})


@knowledge_bp.route('/public/articles/<int:article_id>', methods=['GET'])
def public_article(article_id):
    """前台获取文章详情（仅已发布）"""
    article = KnowledgeArticle.query.get_or_404(article_id)
    if article.status != 1:
        return jsonify({'code': 404, 'message': '该文章未发布'}), 404
    # 增加浏览数
    article.view_count = (article.view_count or 0) + 1
    db.session.commit()
    return jsonify({'code': 200, 'message': 'success', 'data': article.to_dict(include_content=True)})


# ============================================================================
# 分享功能
# ============================================================================

@knowledge_bp.route('/share', methods=['POST'])
@jwt_required_v2
def create_share(current_user):
    """生成分享链接"""
    data = request.get_json() or {}
    node_id = data.get('node_id')
    valid_days = data.get('valid_days', 30)

    node = KnowledgeNode.query.get_or_404(node_id)
    token = make_token()
    share = KnowledgeShare(
        node_id=node_id,
        employee_id=current_user['id'],
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
def list_shares(current_user):
    """我的分享记录"""
    shares = KnowledgeShare.query.filter_by(employee_id=current_user['id']).order_by(
        KnowledgeShare.created_at.desc()
    ).all()
    return jsonify({'code': 200, 'message': 'success', 'data': [s.to_dict() for s in shares]})


# ============================================================================
# 初始化预设数据（V3.3 新增）
# ============================================================================

@knowledge_bp.route('/init/preset', methods=['POST'])
@jwt_required_v2
def init_preset(current_user):
    """初始化预设知识库和分类数据"""
    # 检查是否已初始化（已有非通用分类的知识库）
    existing = KnowledgeBase.query.filter(KnowledgeBase.category.in_(['前端', '中端', '后端', '售后'])).count()
    if existing >= 4:
        return jsonify({'code': 200, 'message': '预设数据已存在，跳过初始化', 'data': {'skipped': True}})

    # 创建4个预设知识库
    preset_bases = [
        {
            'name': '前端：营销与渠道养成',
            'description': '涵盖客户资源获取、渠道养成、工具应用等前端营销知识',
            'category': '前端',
            'icon': 'Search',
            'color': '#409EFF',
            'sort_order': 1,
        },
        {
            'name': '中端：全案设计与谈单',
            'description': '门店赋能、全案规划、全案设计、物料搭配、预算与报价',
            'category': '中端',
            'icon': 'Brush',
            'color': '#67C23A',
            'sort_order': 2,
        },
        {
            'name': '后端：工程、工艺与交付',
            'description': '工艺培训、施工培训、项目监理、项目验收',
            'category': '后端',
            'icon': 'Tools',
            'color': '#E6A23C',
            'sort_order': 3,
        },
        {
            'name': '售后服务',
            'description': '售后服务标准与流程',
            'category': '售后',
            'icon': 'Service',
            'color': '#F56C6C',
            'sort_order': 4,
        },
    ]

    created_bases = []
    for pb in preset_bases:
        base = KnowledgeBase(
            name=pb['name'],
            description=pb['description'],
            category=pb['category'],
            icon=pb['icon'],
            color=pb['color'],
            sort_order=pb['sort_order'],
            status=1,
            author_id=current_user['id'],
        )
        db.session.add(base)
        created_bases.append(base)

    # 创建预设分类（4大类14子类）
    preset_categories = [
        # 一级分类
        {'name': '前端：营销与渠道', 'parent_id': 0, 'level': 1, 'sort_order': 1, 'icon': 'Search', 'color': '#409EFF',
         'children': [
             {'name': '客户资源', 'sort_order': 1},
             {'name': '渠道养成', 'sort_order': 2},
             {'name': '工具应用', 'sort_order': 3},
         ]},
        {'name': '中端：全案设计与谈单', 'parent_id': 0, 'level': 1, 'sort_order': 2, 'icon': 'Brush', 'color': '#67C23A',
         'children': [
             {'name': '门店赋能', 'sort_order': 1},
             {'name': '全案规划', 'sort_order': 2},
             {'name': '全案设计', 'sort_order': 3},
             {'name': '物料搭配', 'sort_order': 4},
             {'name': '预算与报价', 'sort_order': 5},
         ]},
        {'name': '后端：工程与工艺', 'parent_id': 0, 'level': 1, 'sort_order': 3, 'icon': 'Tools', 'color': '#E6A23C',
         'children': [
             {'name': '工艺培训', 'sort_order': 1},
             {'name': '施工培训', 'sort_order': 2},
             {'name': '项目监理', 'sort_order': 3},
             {'name': '项目验收', 'sort_order': 4},
         ]},
        {'name': '售后服务', 'parent_id': 0, 'level': 1, 'sort_order': 4, 'icon': 'Service', 'color': '#F56C6C',
         'children': [
             {'name': '售后标准', 'sort_order': 1},
         ]},
    ]

    for pc in preset_categories:
        parent = KnowledgeCategory(
            name=pc['name'],
            parent_id=0,
            level=1,
            sort_order=pc['sort_order'],
            icon=pc['icon'],
            color=pc['color'],
        )
        db.session.add(parent)
        db.session.flush()  # 获取ID

        for child in pc.get('children', []):
            cat = KnowledgeCategory(
                name=child['name'],
                parent_id=parent.id,
                level=2,
                sort_order=child['sort_order'],
            )
            db.session.add(cat)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '初始化成功',
        'data': {
            'bases': [b.to_dict() for b in created_bases],
            'categories_count': KnowledgeCategory.query.count(),
        }
    })


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
