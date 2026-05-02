"""
客户方案模型 - 存储客户自主选品提交的方案
与后台报价逻辑保持一致
"""
from datetime import datetime
from app import db


class CustomerScheme(db.Model):
    """客户方案主表 - 与Quote结构对齐"""
    __tablename__ = 'customer_schemes'
    # 使用主数据库

    id = db.Column(db.Integer, primary_key=True)
    scheme_no = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='方案编号')
    name = db.Column(db.String(100), nullable=False, comment='方案名称')

    # 客户信息（可选，未登录客户为空）
    customer_id = db.Column(db.Integer, nullable=True, comment='关联客户ID')
    customer_name = db.Column(db.String(50), nullable=True, comment='客户姓名')
    customer_phone = db.Column(db.String(20), nullable=True, comment='客户电话')

    # 方案需求信息
    style = db.Column(db.String(50), nullable=True, comment='期望风格')
    area = db.Column(db.String(20), nullable=True, comment='房屋面积')
    stage = db.Column(db.String(50), nullable=True, comment='装修阶段')
    remark = db.Column(db.Text, nullable=True, comment='需求备注')

    # 分类汇总 - 与Quote.category_summary保持一致
    category_summary = db.Column(db.JSON, default=dict, comment='分类汇总')
    # {
    #   hard_material: {name: '硬装主材', amount: 50000},
    #   construction: {name: '施工服务', amount: 30000},
    #   custom: {name: '全屋定制', amount: 60000},
    #   furniture: {name: '成品家具', amount: 40000},
    #   soft: {name: '软装饰品', amount: 15000},
    #   equipment: {name: '电气设备', amount: 25000},
    # }

    # 费用汇总 - 与Quote保持一致
    subtotal = db.Column(db.Numeric(12, 2), default=0, comment='小计')
    management_fee = db.Column(db.Numeric(12, 2), default=0, comment='管理费')
    management_fee_rate = db.Column(db.Numeric(5, 2), default=0, comment='管理费率%')
    tax = db.Column(db.Numeric(12, 2), default=0, comment='税费')
    tax_rate = db.Column(db.Numeric(5, 2), default=0, comment='税率%')
    total_amount = db.Column(db.Numeric(12, 2), default=0, comment='总价')

    # 统计信息
    total_quantity = db.Column(db.Integer, default=0, comment='产品总数')
    room_count = db.Column(db.Integer, default=0, comment='空间数量')

    # 状态 - 与Quote.status保持一致
    status = db.Column(db.String(20), default='draft', comment='状态')
    # draft(草稿)/submitted(已提交)/processing(处理中)/quoted(已报价)/confirmed(已确认)/cancelled(已取消)

    source = db.Column(db.String(20), default='customer', comment='来源：customer-客户自主, staff-员工创建')

    # 处理信息
    handler_id = db.Column(db.Integer, nullable=True, comment='处理人ID')
    handler_name = db.Column(db.String(50), nullable=True, comment='处理人姓名')
    handled_at = db.Column(db.DateTime, nullable=True, comment='处理时间')
    handle_remark = db.Column(db.Text, nullable=True, comment='处理备注')

    # 关联报价单
    quote_id = db.Column(db.Integer, nullable=True, comment='关联报价单ID')
    quote_no = db.Column(db.String(50), nullable=True, comment='关联报价单编号')

    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'scheme_no': self.scheme_no,
            'name': self.name,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'style': self.style,
            'area': self.area,
            'stage': self.stage,
            'remark': self.remark,
            'category_summary': self.category_summary or {},
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'management_fee': float(self.management_fee) if self.management_fee else 0,
            'management_fee_rate': float(self.management_fee_rate) if self.management_fee_rate else 0,
            'tax': float(self.tax) if self.tax else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'total_quantity': self.total_quantity,
            'room_count': self.room_count,
            'status': self.status,
            'source': self.source,
            'handler_id': self.handler_id,
            'handler_name': self.handler_name,
            'handled_at': self.handled_at.isoformat() if self.handled_at else None,
            'handle_remark': self.handle_remark,
            'quote_id': self.quote_id,
            'quote_no': self.quote_no,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_items:
            items = SchemeItem.query.filter_by(scheme_id=self.id).order_by(SchemeItem.sort_order).all()
            data['items'] = [item.to_dict() for item in items]

        return data


class SchemeItem(db.Model):
    """方案明细表 - 与QuoteItem结构对齐"""
    __tablename__ = 'scheme_items'
    # 使用主数据库

    id = db.Column(db.Integer, primary_key=True)
    scheme_id = db.Column(db.Integer, db.ForeignKey('customer_schemes.id'), nullable=False, comment='方案ID')

    # 空间/房间 - 与QuoteItem.room_name保持一致
    room_name = db.Column(db.String(50), nullable=True, comment='空间/房间名称')

    # 三级分类 - 与QuoteItem保持一致
    category_level1 = db.Column(db.String(50), nullable=True, comment='一级分类')
    category_level2 = db.Column(db.String(50), nullable=True, comment='二级分类')
    category_level3 = db.Column(db.String(50), nullable=True, comment='三级分类')

    # SKU信息（快照，防止后续SKU修改）
    sku_id = db.Column(db.Integer, nullable=False, comment='SKU ID')
    name = db.Column(db.String(200), nullable=False, comment='产品名称')
    sku_code = db.Column(db.String(50), nullable=True, comment='SKU编码')
    spec = db.Column(db.String(200), nullable=True, comment='规格')
    brand = db.Column(db.String(100), nullable=True, comment='品牌')
    unit = db.Column(db.String(20), nullable=True, comment='单位')
    main_image = db.Column(db.String(500), nullable=True, comment='主图')

    # 价格信息
    quantity = db.Column(db.Integer, default=1, comment='数量')
    unit_price = db.Column(db.Numeric(10, 2), default=0, comment='单价')
    total_price = db.Column(db.Numeric(12, 2), default=0, comment='小计')

    # 工艺信息（预留，客户选品暂不用）
    craft_type = db.Column(db.String(100), nullable=True, comment='工艺类型')
    craft_price = db.Column(db.Numeric(10, 2), default=0, comment='工艺价格')

    # 备注
    remark = db.Column(db.String(500), nullable=True, comment='备注')

    # 排序
    sort_order = db.Column(db.Integer, default=0, comment='排序')

    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'scheme_id': self.scheme_id,
            'room_name': self.room_name,
            'category_level1': self.category_level1,
            'category_level2': self.category_level2,
            'category_level3': self.category_level3,
            'sku_id': self.sku_id,
            'name': self.name,
            'sku_code': self.sku_code,
            'spec': self.spec,
            'brand': self.brand,
            'unit': self.unit,
            'main_image': self.main_image,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'craft_type': self.craft_type,
            'craft_price': float(self.craft_price) if self.craft_price else 0,
            'remark': self.remark,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
