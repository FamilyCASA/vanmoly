"""
门店私库物料 - 数据模型
V3.2 报价管理升级新增模块
"""
from datetime import datetime
from app import db


class MaterialStorePrivate(db.Model):
    """门店私库物料表"""
    __tablename__ = 'material_store_private'
    __bind_key__ = 'material'  # 使用物料库

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, comment='门店ID')
    sku_code = db.Column(db.String(50), comment='物料编号')
    name = db.Column(db.String(200), nullable=False, comment='物料名称')
    category_id = db.Column(db.Integer, comment='物料分类')
    image = db.Column(db.String(500), comment='物料主图')
    unit_price = db.Column(db.Numeric(10, 2), default=0, comment='单价')
    unit = db.Column(db.String(20), comment='单位')
    specification = db.Column(db.String(200), comment='规格')
    material = db.Column(db.String(200), comment='材质')
    brand = db.Column(db.String(100), comment='品牌')
    color = db.Column(db.String(100), comment='花色')
    remark = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    import_source = db.Column(db.String(200), comment='来源（记录从哪个报价导入）')
    tenant_id = db.Column(db.String(32), default='0', index=True)

    __table_args__ = (
        db.UniqueConstraint('store_id', 'sku_code', name='uix_store_sku'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'sku_code': self.sku_code,
            'name': self.name,
            'category_id': self.category_id,
            'image': self.image,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'unit': self.unit,
            'specification': self.specification,
            'material': self.material,
            'brand': self.brand,
            'color': self.color,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'import_source': self.import_source,
            'tenant_id': self.tenant_id,
        }