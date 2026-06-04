"""
客户关系管理系统 V2.0 模型
数据库：crm.db
线索转化后数据写入此库
"""
from datetime import datetime
from app import db


class Customer(db.Model):
    """客户表 - 线索转化后写入"""
    __tablename__ = 'customer'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_no = db.Column(db.String(30), unique=True, nullable=False, comment='客户编号')
    
    # 来源线索
    source_lead_id = db.Column(db.Integer, comment='来源线索ID(lead.db)')
    source_lead_no = db.Column(db.String(30), comment='来源线索编号')
    
    # 基本信息
    name = db.Column(db.String(50), nullable=False, comment='客户姓名')
    phone = db.Column(db.String(20), nullable=False, comment='手机号')
    phone_secondary = db.Column(db.String(20), comment='备用电话')
    wechat = db.Column(db.String(50), comment='微信号')
    email = db.Column(db.String(100), comment='邮箱')
    
    # 客户类型
    customer_type = db.Column(db.String(20), default='individual', comment='individual/corporate')
    company_name = db.Column(db.String(100), comment='公司名称')
    
    # 需求信息
    building_name = db.Column(db.String(100), comment='意向楼盘')
    house_type = db.Column(db.String(50), comment='户型')
    area = db.Column(db.Numeric(8, 2), comment='面积')
    budget = db.Column(db.Numeric(12, 2), comment='预算')
    style_preference = db.Column(db.String(100), comment='风格偏好')
    
    # 地址
    province = db.Column(db.String(50), comment='省')
    city = db.Column(db.String(50), comment='市')
    district = db.Column(db.String(50), comment='区')
    address = db.Column(db.String(200), comment='详细地址')
    
    # 归属
    owner_id = db.Column(db.Integer, comment='归属员工ID')
    owner_name = db.Column(db.String(50), comment='归属员工姓名')
    
    # 客户等级
    level = db.Column(db.String(10), default='B', comment='S/A/B/C/D')
    
    # 状态
    status = db.Column(db.String(20), default='active', comment='
        active-活跃
        quoted-已报价
        contracted-已签约
        completed-已完成
        lost-流失
        inactive- inactive
    ')
    
    # 交易统计
    total_contracts = db.Column(db.Integer, default=0, comment='合同数')
    total_amount = db.Column(db.Numeric(14, 2), default=0, comment='累计金额')
    last_deal_at = db.Column(db.DateTime, comment='最后成交时间')
    
    # 标签
    tags = db.Column(db.JSON, default=list, comment='标签')
    
    # 备注
    remark = db.Column(db.Text, comment='备注')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    converted_at = db.Column(db.DateTime, comment='转化时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_no': self.customer_no,
            'source_lead_id': self.source_lead_id,
            'source_lead_no': self.source_lead_no,
            'name': self.name,
            'phone': self.phone,
            'wechat': self.wechat,
            'email': self.email,
            'customer_type': self.customer_type,
            'company_name': self.company_name,
            'building_name': self.building_name,
            'house_type': self.house_type,
            'area': float(self.area) if self.area else None,
            'budget': float(self.budget) if self.budget else None,
            'style_preference': self.style_preference,
            'address': f"{self.province or ''}{self.city or ''}{self.district or ''}{self.address or ''}",
            'owner_id': self.owner_id,
            'owner_name': self.owner_name,
            'level': self.level,
            'status': self.status,
            'total_contracts': self.total_contracts,
            'total_amount': float(self.total_amount),
            'tags': self.tags or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'converted_at': self.converted_at.isoformat() if self.converted_at else None
        }


class CustomerFollow(db.Model):
    """客户跟进记录"""
    __tablename__ = 'customer_follow'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    
    follow_type = db.Column(db.String(20), comment='phone/wechat/visit/meeting')
    content = db.Column(db.Text, nullable=False)
    
    # 结果
    result = db.Column(db.String(20), comment='success/fail/pending')
    next_follow_at = db.Column(db.DateTime, comment='下次跟进时间')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, comment='跟进人')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'follow_type': self.follow_type,
            'content': self.content,
            'result': self.result,
            'next_follow_at': self.next_follow_at.isoformat() if self.next_follow_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CustomerServiceHistory(db.Model):
    """客户服务历史"""
    __tablename__ = 'customer_service_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    
    # 服务信息
    service_type = db.Column(db.String(30), comment='quote/contract/construction/aftersale')
    service_name = db.Column(db.String(100), comment='服务名称')
    related_id = db.Column(db.Integer, comment='关联记录ID')
    related_no = db.Column(db.String(50), comment='关联编号')
    
    # 金额
    amount = db.Column(db.Numeric(12, 2), comment='金额')
    
    # 状态
    status = db.Column(db.String(20), comment='服务状态')
    
    # 时间
    started_at = db.Column(db.DateTime, comment='开始时间')
    completed_at = db.Column(db.DateTime, comment='完成时间')
    
    description = db.Column(db.Text, comment='描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'service_type': self.service_type,
            'service_name': self.service_name,
            'related_no': self.related_no,
            'amount': float(self.amount) if self.amount else None,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
