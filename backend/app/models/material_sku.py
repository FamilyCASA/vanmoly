"""
物料管理模块 - SKU/产品数据模型
V3.0 全新设计，不沿用旧系统界面
"""
from datetime import datetime
from app import db
import json


class MaterialCategory(db.Model):
    """物料分类"""
    __tablename__ = 'material_category'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    # 分类信息
    name = db.Column(db.String(50), nullable=False, comment='分类名称')
    code = db.Column(db.String(20), unique=True, comment='分类编码')
    parent_id = db.Column(db.Integer, db.ForeignKey('material_category.id'), comment='父分类ID')
    level = db.Column(db.Integer, default=1, comment='层级')

    # 样式配置
    icon = db.Column(db.String(100), comment='图标')
    color = db.Column(db.String(20), default='#8B5A2B', comment='主题色')
    sort_order = db.Column(db.Integer, default=0, comment='排序')

    # 状态
    is_enabled = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    parent = db.relationship('MaterialCategory', remote_side=[id], backref='children')
    materials = db.relationship('MaterialSKU', backref='category', lazy='dynamic')

    def to_dict(self):
        # 计算该分类下前台展示物料数
        public_count = 0
        try:
            public_count = self.materials.filter_by(is_deleted=False, is_public=True).count()
        except:
            pass
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'level': self.level,
            'icon': self.icon,
            'color': self.color,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'public_count': public_count,
            'children': [c.to_dict() for c in (self.children or []) if not c.is_deleted] if (self.children or []) else []
        }


class MaterialSKU(db.Model):
    """物料/SKU 主表"""
    __tablename__ = 'material_sku'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    # 基础信息
    sku_code = db.Column(db.String(50), unique=True, nullable=False, comment='SKU编码')
    name = db.Column(db.String(200), nullable=False, comment='产品名称')
    category_id = db.Column(db.Integer, db.ForeignKey('material_category.id'), comment='分类ID')

    # 产品属性
    brand = db.Column(db.String(50), comment='品牌')
    model = db.Column(db.String(100), comment='型号')
    specification = db.Column(db.String(200), comment='规格参数')
    material = db.Column(db.String(100), comment='材质')
    origin = db.Column(db.String(100), comment='产地')

    # 图片
    main_image = db.Column(db.String(500), comment='主图')
    images = db.Column(db.JSON, default=list, comment='图片列表')

    # 价格
    cost_price = db.Column(db.Numeric(10, 2), default=0, comment='成本价')
    sale_price = db.Column(db.Numeric(10, 2), default=0, comment='销售价')
    market_price = db.Column(db.Numeric(10, 2), comment='市场价')

    # 单位
    unit = db.Column(db.String(20), default='件', comment='单位')
    calc_type = db.Column(db.String(20), default='quantity', comment='计价方式:quantity/area/length')

    # 库存
    stock_quantity = db.Column(db.Integer, default=0, comment='库存数量')
    stock_warning = db.Column(db.Integer, default=10, comment='库存预警值')

    # 定制规则 (JSON)
    customization_rules = db.Column(db.JSON, default=list, comment='定制规则')
    # 示例: [
    #   {"type": "coefficient", "name": "系数加价", "field": "coefficient", "default": 1.0},
    #   {"type": "fee", "name": "固定费用", "field": "fixed_fee", "default": 0},
    #   {"type": "increment", "name": "增量计价", "field": "increment", "step": 10, "price_per_step": 100}
    # ]

    # 变体配置
    has_variants = db.Column(db.Boolean, default=False, comment='是否有变体')
    variant_options = db.Column(db.JSON, default=list, comment='变体选项定义')
    # 示例: [{"name": "颜色", "values": ["白色", "黑色", "木色"]}, {"name": "尺寸", "values": ["1.2m", "1.5m", "1.8m"]}]

    # 工艺子物料
    has_craft_parts = db.Column(db.Boolean, default=False, comment='是否有工艺子物料')
    craft_parts = db.Column(db.JSON, default=list, comment='工艺子物料配置')
    # 示例: [{"name": "封边", "material_id": 123, "coefficient": 0.1}]

    # 描述
    description = db.Column(db.Text, comment='产品描述')
    detail_content = db.Column(db.Text, comment='富文本详情内容(HTML)')
    tags = db.Column(db.JSON, default=list, comment='标签')

    # 状态
    status = db.Column(db.String(20), default='active', comment='状态:active/discontinued/draft')
    is_public = db.Column(db.Boolean, default=True, comment='是否前台展示')
    is_deleted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, comment='创建人ID')

    # 关联（跨数据库，不使用外键约束）
    # creator = db.relationship('Employee', lazy='joined')
    variants = db.relationship('MaterialVariant', backref='sku', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_variants=False):
        data = {
            'id': self.id,
            'sku_code': self.sku_code,
            'name': self.name,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'brand': self.brand,
            'model': self.model,
            'specification': self.specification,
            'material': self.material,
            'origin': self.origin,
            'main_image': self.main_image,
            'images': self.images or [],
            'cost_price': float(self.cost_price) if self.cost_price else 0,
            'sale_price': float(self.sale_price) if self.sale_price else 0,
            'market_price': float(self.market_price) if self.market_price else None,
            'unit': self.unit,
            'calc_type': self.calc_type,
            'stock_quantity': self.stock_quantity or 0,
            'stock_warning': self.stock_warning or 10,
            'customization_rules': self.customization_rules or [],
            'has_variants': self.has_variants,
            'variant_options': self.variant_options or [],
            'has_craft_parts': self.has_craft_parts,
            'craft_parts': self.craft_parts or [],
            'description': self.description,
            'detail_content': self.detail_content,
            'tags': self.tags or [],
            'status': self.status,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_variants:
            data['variants'] = [v.to_dict() for v in self.variants]
        return data


class MaterialVariant(db.Model):
    """物料变体（花色、尺寸等）"""
    __tablename__ = 'material_variant'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku_id = db.Column(db.Integer, db.ForeignKey('material_sku.id'), nullable=False)

    # 变体属性
    variant_code = db.Column(db.String(50), comment='变体编码')
    variant_name = db.Column(db.String(100), comment='变体名称')
    variant_values = db.Column(db.JSON, comment='变体属性值 {"颜色": "白色", "尺寸": "1.5m"}')

    # 变体图片
    image = db.Column(db.String(500), comment='变体图片')

    # 变体价格调整
    price_adjustment = db.Column(db.Numeric(10, 2), default=0, comment='价格调整')

    # 库存
    stock_quantity = db.Column(db.Integer, default=0)

    # 状态
    is_enabled = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'sku_id': self.sku_id,
            'variant_code': self.variant_code,
            'variant_name': self.variant_name,
            'variant_values': self.variant_values or {},
            'image': self.image,
            'price_adjustment': float(self.price_adjustment) if self.price_adjustment else 0,
            'stock_quantity': self.stock_quantity or 0,
            'is_enabled': self.is_enabled,
        }


class MaterialSupplier(db.Model):
    """供应商信息"""
    __tablename__ = 'material_supplier'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    name = db.Column(db.String(100), nullable=False, comment='供应商名称')
    contact_person = db.Column(db.String(50), comment='联系人')
    phone = db.Column(db.String(20), comment='电话')
    email = db.Column(db.String(100), comment='邮箱')
    address = db.Column(db.String(255), comment='地址')

    # 合作状态
    status = db.Column(db.String(20), default='active', comment='状态')
    remark = db.Column(db.Text, comment='备注')

    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'status': self.status,
            'remark': self.remark,
        }


# 计价方式选项
CALC_TYPES = [
    {'value': 'quantity', 'label': '按数量', 'unit': '件'},
    {'value': 'area', 'label': '按面积', 'unit': '㎡'},
    {'value': 'length', 'label': '按长度', 'unit': 'm'},
    {'value': 'volume', 'label': '按体积', 'unit': 'm³'},
]

# 定制规则类型
CUSTOMIZATION_RULE_TYPES = [
    {'value': 'coefficient', 'label': '系数加价', 'desc': '基础价格 × 系数'},
    {'value': 'fee', 'label': '固定费用', 'desc': '基础价格 + 固定金额'},
    {'value': 'increment', 'label': '增量计价', 'desc': '每增加单位长度/面积，增加对应价格'},
]

# SKU 状态
SKU_STATUS = [
    {'value': 'active', 'label': '在售', 'type': 'success'},
    {'value': 'discontinued', 'label': '停售', 'type': 'info'},
    {'value': 'draft', 'label': '草稿', 'type': 'warning'},
    {'value': 'out_of_stock', 'label': '缺货', 'type': 'danger'},
]
