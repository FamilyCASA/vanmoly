# -*- coding: utf-8 -*-
"""
商学院知识库模块 - 数据模型
VANMOLY-SYS V3.3 知识库全面升级
"""
from datetime import datetime
from app import db


class KnowledgeBase(db.Model):
    """知识库"""
    __tablename__ = 'knowledge_base'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='知识库名称')
    description = db.Column(db.String(500), default='', comment='知识库描述')
    cover_image = db.Column(db.String(500), default='', comment='封面图')
    related_module = db.Column(db.String(50), default='', comment='关联模块')
    status = db.Column(db.Integer, default=1, comment='状态 0=停用 1=启用')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # V3.3 新增字段
    category = db.Column(db.String(50), default='通用', comment='知识库大类（前端营销/中端设计/后端施工/售后服务/通用）')
    icon = db.Column(db.String(100), default='Document', comment='图标名（Element Plus图标名）')
    color = db.Column(db.String(20), default='#409EFF', comment='主题色')
    tags = db.Column(db.JSON, default=list, comment='标签列表')
    author_id = db.Column(db.Integer, comment='创建者员工ID')
    view_count = db.Column(db.Integer, default=0, comment='总浏览数')
    is_public = db.Column(db.Boolean, default=False, comment='是否公开')

    nodes = db.relationship('KnowledgeNode', backref='base', lazy='dynamic',
                            order_by='KnowledgeNode.sort_order',
                            cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'cover_image': self.cover_image or '',
            'related_module': self.related_module or '',
            'status': self.status,
            'sort_order': self.sort_order,
            'node_count': self.nodes.count(),
            # V3.3 新增
            'category': self.category or '通用',
            'icon': self.icon or 'Document',
            'color': self.color or '#409EFF',
            'tags': self.tags or [],
            'author_id': self.author_id,
            'view_count': self.view_count or 0,
            'is_public': self.is_public or False,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else '',
        }


class KnowledgeNode(db.Model):
    """知识库节点（树状结构，最多三层）"""
    __tablename__ = 'knowledge_node'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    base_id = db.Column(db.Integer, db.ForeignKey('knowledge_base.id', ondelete='CASCADE'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('knowledge_node.id', ondelete='CASCADE'), default=0, index=True, comment='父节点ID，0=根节点')
    node_name = db.Column(db.String(200), nullable=False, comment='节点名称')
    level = db.Column(db.Integer, default=1, comment='层级 1=一级标题 2=二级章节 3=三级小节')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    status = db.Column(db.Integer, default=1, comment='状态 0=隐藏 1=展示')
    content = db.Column(db.Text, default='', comment='第四层文案内容（HTML）')
    file_ids = db.Column(db.JSON, default=list, comment='关联文件ID列表')
    video_url = db.Column(db.String(500), default='', comment='视频URL')
    view_count = db.Column(db.Integer, default=0, comment='浏览次数')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # V3.3 新增字段
    summary = db.Column(db.String(500), default='', comment='摘要')
    cover_image = db.Column(db.String(500), default='', comment='封面图')
    tags = db.Column(db.JSON, default=list, comment='标签')
    author_id = db.Column(db.Integer, comment='作者')
    word_count = db.Column(db.Integer, default=0, comment='字数统计')
    is_featured = db.Column(db.Boolean, default=False, comment='是否精选')
    sort_type = db.Column(db.String(20), default='manual', comment='排序方式(manual/time/views)')

    children = db.relationship('KnowledgeNode',
                                backref=db.backref('parent_node', remote_side=[id]),
                                lazy='dynamic',
                                order_by='KnowledgeNode.sort_order',
                                foreign_keys='KnowledgeNode.parent_id')

    # 与文章的关联
    articles = db.relationship('KnowledgeArticle', backref='node', lazy='dynamic',
                               cascade='all, delete-orphan',
                               order_by='KnowledgeArticle.sort_order')

    def to_dict(self, include_children=False, include_content=False, include_article_count=False):
        result = {
            'id': self.id,
            'base_id': self.base_id,
            'parent_id': self.parent_id,
            'node_name': self.node_name,
            'level': self.level,
            'sort_order': self.sort_order,
            'status': self.status,
            'file_ids': self.file_ids or [],
            'video_url': self.video_url or '',
            'view_count': self.view_count,
            # V3.3 新增
            'summary': self.summary or '',
            'cover_image': self.cover_image or '',
            'tags': self.tags or [],
            'author_id': self.author_id,
            'word_count': self.word_count or 0,
            'is_featured': self.is_featured or False,
            'sort_type': self.sort_type or 'manual',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else '',
        }
        if include_content:
            result['content'] = self.content or ''
        if include_article_count:
            result['article_count'] = self.articles.count()
        if include_children:
            result['children'] = [c.to_dict(include_children=True, include_content=True, include_article_count=True)
                                   for c in self.children.order_by('sort_order').all()]
        return result


class KnowledgeArticle(db.Model):
    """知识库文章（挂在三级节点下）"""
    __tablename__ = 'knowledge_article'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    node_id = db.Column(db.Integer, db.ForeignKey('knowledge_node.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, comment='标题')
    content = db.Column(db.Text, default='', comment='HTML正文')
    summary = db.Column(db.String(500), default='', comment='摘要')
    cover_image = db.Column(db.String(500), default='', comment='封面图')
    video_url = db.Column(db.String(500), default='', comment='视频URL')
    file_ids = db.Column(db.JSON, default=list, comment='附件文件ID列表')
    tags = db.Column(db.JSON, default=list, comment='标签')
    author_id = db.Column(db.Integer, comment='作者员工ID')
    status = db.Column(db.Integer, default=1, comment='0=草稿 1=已发布 2=待审')
    view_count = db.Column(db.Integer, default=0, comment='浏览数')
    like_count = db.Column(db.Integer, default=0, comment='点赞数')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_content=False):
        result = {
            'id': self.id,
            'node_id': self.node_id,
            'title': self.title,
            'summary': self.summary or '',
            'cover_image': self.cover_image or '',
            'video_url': self.video_url or '',
            'file_ids': self.file_ids or [],
            'tags': self.tags or [],
            'author_id': self.author_id,
            'status': self.status,
            'view_count': self.view_count or 0,
            'like_count': self.like_count or 0,
            'sort_order': self.sort_order or 0,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else '',
        }
        if include_content:
            result['content'] = self.content or ''
        return result


class KnowledgeCategory(db.Model):
    """知识库分类"""
    __tablename__ = 'knowledge_category'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, comment='分类名称')
    parent_id = db.Column(db.Integer, db.ForeignKey('knowledge_category.id', ondelete='CASCADE'), default=0, index=True, comment='父分类ID，0=根分类')
    level = db.Column(db.Integer, default=1, comment='层级')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    icon = db.Column(db.String(100), default='', comment='图标名')
    color = db.Column(db.String(20), default='', comment='主题色')
    description = db.Column(db.String(200), default='', comment='描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    children = db.relationship('KnowledgeCategory',
                                backref=db.backref('parent_cat', remote_side=[id]),
                                lazy='dynamic',
                                order_by='KnowledgeCategory.sort_order',
                                foreign_keys='KnowledgeCategory.parent_id')

    def to_dict(self, include_children=False):
        result = {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'level': self.level,
            'sort_order': self.sort_order,
            'icon': self.icon or '',
            'color': self.color or '',
            'description': self.description or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }
        if include_children:
            result['children'] = [c.to_dict(include_children=True)
                                   for c in self.children.order_by('sort_order').all()]
        return result


class KnowledgeShare(db.Model):
    """知识库分享记录"""
    __tablename__ = 'knowledge_share'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    node_id = db.Column(db.Integer, db.ForeignKey('knowledge_node.id', ondelete='CASCADE'), nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, index=True)
    share_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    valid_days = db.Column(db.Integer, default=30, comment='有效期天数')
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expire_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'node_id': self.node_id,
            'employee_id': self.employee_id,
            'share_token': self.share_token,
            'valid_days': self.valid_days,
            'view_count': self.view_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'expire_at': self.expire_at.strftime('%Y-%m-%d %H:%M') if self.expire_at else '',
            'is_expired': datetime.utcnow() > self.expire_at if self.expire_at else False,
        }


# 简化版：前台用户（可后续扩展）
class FrontUser(db.Model):
    """商学院前台用户"""
    __tablename__ = 'front_user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    region = db.Column(db.String(100), default='', comment='所在地区')
    intention = db.Column(db.String(50), default='', comment='意向类型')
    password_hash = db.Column(db.String(128), nullable=False)
    personal_star = db.Column(db.Integer, default=0, comment='个人星星数')
    unlocked_bases = db.Column(db.JSON, default=list, comment='已解锁知识库ID列表')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'region': self.region or '',
            'intention': self.intention or '',
            'personal_star': self.personal_star,
            'unlocked_bases': self.unlocked_bases or [],
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else '',
        }
