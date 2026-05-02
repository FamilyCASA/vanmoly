"""
文章/动态模块数据模型
"""
from datetime import datetime
from app import db


class Article(db.Model):
    """文章/动态表"""
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, comment='标题')
    cover_image = db.Column(db.String(500), comment='封面图')
    summary = db.Column(db.Text, comment='摘要')
    content = db.Column(db.Text, comment='正文')
    tags = db.Column(db.Text, comment='标签JSON')
    type = db.Column(db.String(20), default='动态', comment='类型')
    author_id = db.Column(db.Integer, comment='作者ID')
    view_count = db.Column(db.Integer, default=0, comment='浏览量')
    likes = db.Column(db.Integer, default=0, comment='点赞数')
    status = db.Column(db.String(20), default='草稿', comment='状态')
    is_top = db.Column(db.Boolean, default=False, comment='是否置顶')
    publish_at = db.Column(db.DateTime, comment='发布时间')
    tenant_id = db.Column(db.String(20), comment='租户ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 类型常量
    TYPE_NEWS = '动态'
    TYPE_GUIDE = '攻略'
    TYPE_STORY = '案例故事'

    # 状态常量
    STATUS_DRAFT = '草稿'
    STATUS_PUBLISHED = '已发布'
    STATUS_OFFLINE = '已下线'

    def to_dict(self, include_content=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'cover_image': self.cover_image,
            'summary': self.summary,
            'tags': self.tags,
            'type': self.type,
            'author_id': self.author_id,
            'view_count': self.view_count,
            'likes': self.likes,
            'status': self.status,
            'is_top': self.is_top,
            'publish_at': self.publish_at.isoformat() if self.publish_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_content:
            data['content'] = self.content
            
        return data

    def publish(self):
        """发布文章"""
        self.status = self.STATUS_PUBLISHED
        self.publish_at = datetime.utcnow()
        db.session.commit()

    def increment_view(self):
        """增加浏览量"""
        self.view_count += 1
        db.session.commit()

    def increment_likes(self):
        """增加点赞数"""
        self.likes += 1
        db.session.commit()
