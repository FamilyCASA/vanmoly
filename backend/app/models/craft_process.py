"""
特殊工艺数据库 - 数据模型
独立于物料库，用于全屋定制工艺和硬装施工工艺
"""
from datetime import datetime
from app import db


class CraftProcess(db.Model):
    """特殊工艺"""
    __tablename__ = 'craft_process'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    # 基本信息
    name = db.Column(db.String(200), nullable=False, comment='工艺名称')
    category = db.Column(db.String(50), nullable=False, comment='工艺分类: custom(全屋定制)/construction(硬装施工)')
    code = db.Column(db.String(50), comment='工艺编码')

    # 价格参数
    coefficient = db.Column(db.Numeric(6, 3), default=1, comment='工艺系数')
    unit_price = db.Column(db.Numeric(10, 2), default=0, comment='工艺单价')
    unit = db.Column(db.String(20), default='项', comment='工艺单位')

    # 图片
    main_image = db.Column(db.String(500), comment='主图URL')
    construction_image = db.Column(db.String(500), comment='施工图URL')
    real_image = db.Column(db.String(500), comment='实景图URL')

    # 富文本简介
    description = db.Column(db.Text, comment='工艺简介（富文本HTML）')

    # 状态
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_deleted = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0, comment='排序')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'category': self.category,
            'code': self.code,
            'coefficient': float(self.coefficient) if self.coefficient else 1,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'unit': self.unit or '项',
            'main_image': self.main_image,
            'construction_image': self.construction_image,
            'real_image': self.real_image,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
