"""
报价管理模块 - 数据模型
V3.0 全新设计
"""
from datetime import datetime
from app import db


class Quote(db.Model):
    """报价单主表"""
    __bind_key__ = 'quote'
    __tablename__ = 'quote'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    # 报价编号
    quote_no = db.Column(db.String(50), unique=True, nullable=False, comment='报价编号')

    # 关联
    customer_id = db.Column(db.Integer, nullable=False, comment='客户ID')
    customer_name = db.Column(db.String(100), comment='客户姓名(冗余)')
    customer_phone = db.Column(db.String(20), comment='客户电话(冗余)')

    # 封面配置
    cover_config = db.Column(db.JSON, default=dict, comment='封面配置')
    # {
    #   template: 'modern/classic/minimal',  // 模板风格
    #   primary_color: '#8B4513',            // 主色调
    #   background_image: 'url',             // 背景图片
    #   logo: 'url',                         // Logo
    #   watermark: 'D&B 帝标|设记家全案服务',         // 水印文字
    #   show_customer_info: true,            // 显示客户信息
    #   show_store_name: true,               // 显示门店名称
    #   store_name: 'D&B 帝标|设记家·全安落地服务中心',   // 门店名称
    # }

    # 服务团队
    service_team = db.Column(db.JSON, default=list, comment='服务团队')
    # [
    #   {role: 'planner', role_name: '全案规划师', employee_id: 1, name: '张三', phone: '138...'},
    #   {role: 'designer_3d', role_name: '效果图设计师', employee_id: 2, name: '李四', phone: '139...'},
    #   ...
    # ]

    # 报价分类汇总
    category_summary = db.Column(db.JSON, default=dict, comment='分类汇总')
    # {
    #   hard_material: {name: '硬装主材', amount: 50000},
    #   construction: {name: '施工服务', amount: 30000},
    #   installation: {name: '安装服务', amount: 8000},
    #   delivery: {name: '配送服务', amount: 5000},
    #   moving: {name: '搬运服务', amount: 3000},
    #   design: {name: '设计服务', amount: 20000},
    #   custom: {name: '全屋定制', amount: 60000},
    #   furniture: {name: '成品家具', amount: 40000},
    #   soft: {name: '软装饰品', amount: 15000},
    #   equipment: {name: '电气设备', amount: 25000},
    # }

    # 费用汇总
    subtotal = db.Column(db.Numeric(12, 2), default=0, comment='小计')
    management_fee = db.Column(db.Numeric(12, 2), default=0, comment='管理费')
    management_fee_rate = db.Column(db.Numeric(5, 2), default=0, comment='管理费率%')
    tax = db.Column(db.Numeric(12, 2), default=0, comment='税费')
    tax_rate = db.Column(db.Numeric(5, 2), default=0, comment='税率%')
    total_amount = db.Column(db.Numeric(12, 2), default=0, comment='总价')

    # 签字信息
    signature_customer = db.Column(db.String(255), comment='客户签名')
    signature_planner = db.Column(db.String(255), comment='规划师签名')
    signature_manager = db.Column(db.String(255), comment='店长签名')
    signature_seal = db.Column(db.String(255), comment='电子公章')
    signed_at = db.Column(db.DateTime, comment='签署时间')

    # 状态
    status = db.Column(db.String(20), default='draft', comment='状态')
    # draft(草稿)/sent(已发送)/confirmed(已确认)/signed(已签署)/expired(已过期)

    # 有效期
    valid_days = db.Column(db.Integer, default=30, comment='有效期天数')
    expire_date = db.Column(db.Date, comment='过期日期')

    # 创建人
    creator_id = db.Column(db.Integer, comment='创建人ID')
    creator_name = db.Column(db.String(50), comment='创建人姓名')

    remark = db.Column(db.Text, comment='备注')
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'quote_no': self.quote_no,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'cover_config': self.cover_config or {},
            'service_team': self.service_team or [],
            'category_summary': self.category_summary or {},
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'management_fee': float(self.management_fee) if self.management_fee else 0,
            'management_fee_rate': float(self.management_fee_rate) if self.management_fee_rate else 0,
            'tax': float(self.tax) if self.tax else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'signature_customer': self.signature_customer,
            'signature_planner': self.signature_planner,
            'signature_manager': self.signature_manager,
            'signature_seal': self.signature_seal,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None,
            'status': self.status,
            'valid_days': self.valid_days,
            'expire_date': self.expire_date.isoformat() if self.expire_date else None,
            'creator_id': self.creator_id,
            'creator_name': self.creator_name,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

        if include_items:
            items = QuoteItem.query.filter_by(quote_id=self.id).all()
            data['items'] = [item.to_dict() for item in items]

        return data


class QuoteItem(db.Model):
    """报价单项"""
    __bind_key__ = 'quote'
    __tablename__ = 'quote_item'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quote.id'), nullable=False)

    # 房间分类
    room_name = db.Column(db.String(50), comment='房间名称')
    # 客厅/主卧/次卧/书房/厨房/卫生间/阳台/玄关/餐厅等

    # 三级分类
    category_level1 = db.Column(db.String(50), comment='大类')
    category_level2 = db.Column(db.String(50), comment='中类')
    category_level3 = db.Column(db.String(50), comment='小类')

    # 物料/服务信息
    item_type = db.Column(db.String(20), comment='类型')
    # product(产品)/service(服务)/package(套餐)

    sku_id = db.Column(db.Integer, comment='关联SKU ID')

    name = db.Column(db.String(200), nullable=False, comment='名称')
    spec = db.Column(db.String(200), comment='规格')
    brand = db.Column(db.String(100), comment='品牌')
    unit = db.Column(db.String(20), comment='单位')

    # 价格
    quantity = db.Column(db.Numeric(10, 2), default=1, comment='数量')
    unit_price = db.Column(db.Numeric(10, 2), default=0, comment='单价')
    total_price = db.Column(db.Numeric(12, 2), default=0, comment='总价')

    # 工艺/定制
    craft_type = db.Column(db.String(50), comment='工艺类型')
    craft_price = db.Column(db.Numeric(10, 2), default=0, comment='工艺费')

    # 图片
    image = db.Column(db.String(255), comment='图片')

    # 备注
    remark = db.Column(db.Text, comment='备注')

    sort_order = db.Column(db.Integer, default=0, comment='排序')
    tenant_id = db.Column(db.String(32), default='0', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ====== V3.2 增强字段 ======
    # 定制尺寸（mm）
    width = db.Column(db.Numeric(10, 2), comment='宽度mm')
    depth = db.Column(db.Numeric(10, 2), comment='深度mm')
    height = db.Column(db.Numeric(10, 2), comment='高度mm')
    # 计量值：系统根据尺寸自动计算
    measurement_value = db.Column(db.Numeric(12, 4), default=1, comment='计量值')
    # 工艺数量/系数
    craft_quantity = db.Column(db.Numeric(10, 2), default=1, comment='工艺数量')
    craft_coefficient = db.Column(db.Numeric(5, 2), default=1, comment='工艺系数')

    def to_dict(self):
        return {
            'id': self.id,
            'quote_id': self.quote_id,
            'room_name': self.room_name,
            'category_level1': self.category_level1,
            'category_level2': self.category_level2,
            'category_level3': self.category_level3,
            'item_type': self.item_type,
            'sku_id': self.sku_id,
            'name': self.name,
            'spec': self.spec,
            'brand': self.brand,
            'unit': self.unit,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'craft_type': self.craft_type,
            'craft_price': float(self.craft_price) if self.craft_price else 0,
            'image': self.image,
            'remark': self.remark,
            'sort_order': self.sort_order,
            'tenant_id': self.tenant_id,
            # V3.2 增强字段
            'width': float(self.width) if self.width else None,
            'depth': float(self.depth) if self.depth else None,
            'height': float(self.height) if self.height else None,
            'measurement_value': float(self.measurement_value) if self.measurement_value else 1,
            'craft_quantity': float(self.craft_quantity) if self.craft_quantity else 1,
            'craft_coefficient': float(self.craft_coefficient) if self.craft_coefficient else 1,
        }


class QuoteTemplate(db.Model):
    """报价封面模板"""
    __bind_key__ = 'quote'
    __tablename__ = 'quote_template'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    name = db.Column(db.String(50), nullable=False, comment='模板名称')
    template_type = db.Column(db.String(20), default='modern', comment='模板类型')
    # modern(现代)/classic(经典)/minimal(极简)/luxury(奢华)

    # 样式配置
    style_config = db.Column(db.JSON, default=dict, comment='样式配置')
    # {
    #   primary_color: '#8B4513',
    #   secondary_color: '#D2691E',
    #   background_color: '#FFF8DC',
    #   font_family: 'Microsoft YaHei',
    #   title_size: 32,
    #   subtitle_size: 18,
    # }

    # 预设背景图
    background_images = db.Column(db.JSON, default=list, comment='背景图片选项')

    # 水印设置
    watermark_config = db.Column(db.JSON, default=dict, comment='水印配置')
    # {
    #   text: 'D&B 帝标|设记家全案服务',
    #   opacity: 0.1,
    #   font_size: 48,
    #   angle: -45,
    # }

    is_default = db.Column(db.Boolean, default=False, comment='是否默认')
    is_enabled = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'template_type': self.template_type,
            'style_config': self.style_config or {},
            'background_images': self.background_images or [],
            'watermark_config': self.watermark_config or {},
            'is_default': self.is_default,
            'is_enabled': self.is_enabled,
        }


# 报价分类选项
QUOTE_CATEGORIES = [
    ('hard_material', '硬装主材'),
    ('construction', '施工服务'),
    ('installation', '安装服务'),
    ('delivery', '配送服务'),
    ('moving', '搬运服务'),
    ('design', '设计服务'),
    ('custom', '全屋定制'),
    ('furniture', '成品家具'),
    ('soft', '软装饰品'),
    ('equipment', '电气设备'),
    ('smart_home', '智能家居'),
    ('other', '其他'),
]

# 服务团队角色选项
SERVICE_ROLES = [
    ('planner', '全案规划师'),
    ('designer_3d', '效果图设计师'),
    ('designer_cd', '施工图设计师'),
    ('designer_furniture', '家具深化设计师'),
    ('project_manager', '项目经理'),
    ('foreman_civil', '土建工长'),
    ('foreman_electric', '水电工长'),
    ('foreman_tile', '瓦工工长'),
    ('foreman_wood', '木工工长'),
    ('foreman_paint', '油工工长'),
    ('supervisor', '现场督导'),
    ('installer', '安装工程师'),
    ('soft_designer', '软装设计师'),
    ('budget_officer', '预算专员'),
    ('customer_service', '客服专员'),
]

# 房间选项
ROOM_OPTIONS = [
    '客厅',
    '餐厅',
    '主卧',
    '次卧',
    '儿童房',
    '书房',
    '厨房',
    '主卫',
    '客卫',
    '阳台',
    '玄关',
    '衣帽间',
    '储藏室',
    '楼梯间',
    '花园',
    '露台',
]

# 报价状态
QUOTE_STATUS = [
    ('draft', '草稿'),
    ('sent', '已发送'),
    ('confirmed', '已确认'),
    ('signed', '已签署'),
    ('expired', '已过期'),
]
