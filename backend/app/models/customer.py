"""
客户管理模块 - 数据模型
从 vanmoly-distilled 蒸馏而来
"""
from datetime import datetime
from app import db


class Customer(db.Model):
    """客户主表"""
    __tablename__ = 'customer'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True, comment='租户ID')

    # 基础信息
    name = db.Column(db.String(80), nullable=False, comment='客户姓名')
    phone = db.Column(db.String(20), nullable=False, comment='联系电话')
    gender = db.Column(db.String(10), default='未知', comment='性别')
    email = db.Column(db.String(120), comment='邮箱')
    wechat = db.Column(db.String(50), comment='微信')

    # 地址信息
    address = db.Column(db.String(255), comment='完整地址')
    province = db.Column(db.String(50), comment='省份')
    city = db.Column(db.String(50), comment='城市')
    district = db.Column(db.String(50), comment='区县')
    street = db.Column(db.String(100), comment='街道')
    detail_address = db.Column(db.String(255), comment='详细地址（门牌号）')
    building_name = db.Column(db.String(100), comment='楼盘名称')

    # 业务信息
    source = db.Column(db.String(50), comment='来源渠道')
    budget = db.Column(db.String(50), comment='预算区间')
    house_type = db.Column(db.String(50), comment='户型')
    house_area = db.Column(db.Float, comment='面积m²')

    # 需求描述
    requirements = db.Column(db.Text, comment='装修需求')
    style_preference = db.Column(db.String(100), comment='风格偏好')

    # 客户类型 & 状态
    customer_type = db.Column(db.String(20), default='已接触',
                              comment='客户类型:已接触/已拜访/提案已经确认/跟进中/定金已收/已成交')
    status = db.Column(db.String(20), default='待跟进', comment='状态:待跟进/跟进中/已成交/已流失')
    priority = db.Column(db.String(20), default='普通', comment='优先级:普通/重要/紧急')

    # 归属（注意：Employee在hr数据库，此处不用外键约束）
    owner_id = db.Column(db.Integer, comment='跟进人ID')

    # 跟进统计
    follow_count = db.Column(db.Integer, default=0, comment='跟进次数')
    last_follow = db.Column(db.DateTime, comment='最近跟进时间')
    next_follow = db.Column(db.DateTime, comment='下次跟进时间')
    remark = db.Column(db.Text, comment='备注')

    # 软删除
    is_deleted = db.Column(db.Boolean, default=False)

    # 客户账号（用于访客注册登录）
    password_hash = db.Column(db.String(128), comment='密码哈希')
    last_login_at = db.Column(db.DateTime, comment='最后登录时间')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    follows = db.relationship('CustomerFollow', backref='customer', lazy='dynamic',
                              cascade='all, delete-orphan')

    def to_dict(self, include_follows=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'phone': self.phone,
            'gender': self.gender,
            'email': self.email,
            'wechat': self.wechat,
            'address': self.address,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'street': self.street,
            'detail_address': self.detail_address,
            'building_name': self.building_name,
            'source': self.source,
            'budget': self.budget,
            'house_type': self.house_type,
            'house_area': self.house_area,
            'requirements': self.requirements,
            'style_preference': self.style_preference,
            'customer_type': self.customer_type,
            'status': self.status,
            'priority': self.priority,
            'owner_id': self.owner_id,
            'owner_name': None,  # TODO: 手动查询Employee表获取
            'follow_count': self.follow_count or 0,
            'last_follow': self.last_follow.isoformat() if self.last_follow else None,
            'next_follow': self.next_follow.isoformat() if self.next_follow else None,
            'remark': self.remark,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_follows:
            data['follows'] = [f.to_dict() for f in self.follows.order_by(CustomerFollow.created_at.desc())]
        return data


class CustomerFollow(db.Model):
    """客户跟进记录"""
    __tablename__ = 'customer_follow'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

    follow_type = db.Column(db.String(20), comment='跟进方式:电话/微信/到店/其他')
    content = db.Column(db.Text, comment='跟进内容')
    next_follow_at = db.Column(db.DateTime, comment='下次跟进时间')

    operator_id = db.Column(db.Integer, comment='操作人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联（跨数据库，不用relationship）
    # operator = db.relationship('Employee', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'follow_type': self.follow_type,
            'content': self.content,
            'next_follow_at': self.next_follow_at.isoformat() if self.next_follow_at else None,
            'operator_id': self.operator_id,
            'operator_name': self.operator.name if self.operator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# 客户来源选项
CUSTOMER_SOURCES = [
    '线上获客',
    '楼盘调查',
    '老客户推荐',
    '自然进店',
    '合作伙伴',
    '其他'
]

# 客户类型选项
CUSTOMER_TYPES = [
    '已接触',
    '已拜访',
    '提案已经确认',
    '跟进中',
    '定金已收',
    '已成交'
]

# 客户状态选项
CUSTOMER_STATUS = [
    '待跟进',
    '跟进中',
    '已成交',
    '已流失'
]

# 优先级选项
PRIORITY_OPTIONS = ['普通', '重要', '紧急']

# 跟进方式选项
FOLLOW_TYPES = ['电话', '微信', '到店', '其他']
