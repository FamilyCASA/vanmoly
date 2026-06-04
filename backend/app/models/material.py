"""
销售物料模块数据模型
"""
from datetime import datetime
from app import db


class SalesMaterial(db.Model):
    """销售物料表"""
    __tablename__ = 'sales_material'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, comment='物料名称')
    type = db.Column(db.String(20), comment='类型')
    category = db.Column(db.String(50), comment='分类')
    image_url = db.Column(db.String(500), comment='图片URL')
    file_url = db.Column(db.String(500), comment='文件下载URL')
    qr_code_url = db.Column(db.String(500), comment='二维码图片')
    share_title = db.Column(db.String(200), comment='分享标题')
    share_desc = db.Column(db.Text, comment='分享描述')
    status = db.Column(db.String(20), default='启用', comment='状态')
    view_count = db.Column(db.Integer, default=0, comment='浏览次数')
    download_count = db.Column(db.Integer, default=0, comment='下载次数')
    tenant_id = db.Column(db.String(20), comment='租户ID')
    created_by = db.Column(db.Integer, comment='创建人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 类型常量
    TYPE_POSTER = '海报'
    TYPE_MANUAL = '手册'
    TYPE_MATERIAL = '素材'
    TYPE_TEMPLATE = '模板'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'category': self.category,
            'image_url': self.image_url,
            'file_url': self.file_url,
            'qr_code_url': self.qr_code_url,
            'share_title': self.share_title,
            'share_desc': self.share_desc,
            'status': self.status,
            'view_count': self.view_count,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def increment_view(self):
        """增加浏览量"""
        self.view_count += 1
        db.session.commit()

    def increment_download(self):
        """增加下载量"""
        self.download_count += 1
        db.session.commit()
