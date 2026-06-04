# -*- coding: utf-8 -*-
"""
商学院知识库模块 - 数据模型
VANMOLY-SYS V3.2
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

    children = db.relationship('KnowledgeNode',
                                backref=db.backref('parent_node', remote_side=[id]),
                                lazy='dynamic',
                                order_by='KnowledgeNode.sort_order',
                                foreign_keys='KnowledgeNode.parent_id')

    def to_dict(self, include_children=False, include_content=False):
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
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else '',
        }
        if include_content:
            result['content'] = self.content or ''
        if include_children:
            result['children'] = [c.to_dict(include_children=True, include_content=True)
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
