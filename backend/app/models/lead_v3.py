"""
线索管理系统 V3.0 模型
数据库：lead.db
与HR积分系统联动
"""
from datetime import datetime
from app import db


class Lead(db.Model):
    """线索表 - 独立数据库"""
    __tablename__ = 'lead'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lead_no = db.Column(db.String(30), unique=True, nullable=False, comment='线索编号')
    
    # 客户信息
    name = db.Column(db.String(50), nullable=False, comment='客户姓名')
    phone = db.Column(db.String(20), nullable=False, comment='手机号')
    phone_secondary = db.Column(db.String(20), comment='备用电话')
    wechat = db.Column(db.String(50), comment='微信号')
    
    # 需求信息
    building_name = db.Column(db.String(100), comment='意向楼盘')
    house_type = db.Column(db.String(50), comment='户型')
    area = db.Column(db.Numeric(8, 2), comment='面积')
    budget = db.Column(db.Numeric(12, 2), comment='预算')
    style_preference = db.Column(db.String(100), comment='风格偏好')
    
    # 线索状态
    status = db.Column(db.String(20), default='new', comment='
        new-新线索
        assigned-已分配
        contacted-已联系
        followed-跟进中
        appointment_booked-预约到店
        appointment_actual-已到店
        demand_confirmed-需求确认
        quoted-已报价
        deposit_paid-已交定金
        converted-已转化(成交)
        invalid-无效
        public-公海
    ')
    
    # 来源渠道
    source_channel = db.Column(db.String(50), comment='来源渠道')
    source_detail = db.Column(db.String(100), comment='来源详情')
    landing_page = db.Column(db.String(200), comment='落地页')
    utm_source = db.Column(db.String(50))
    utm_medium = db.Column(db.String(50))
    utm_campaign = db.Column(db.String(50))
    
    # 分配信息
    assigned_to = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='分配给员工ID')
    assigned_at = db.Column(db.DateTime, comment='分配时间')
    assigned_by = db.Column(db.Integer, comment='分配人')
    
    # 转化信息
    converted_to_customer_id = db.Column(db.Integer, comment='转化后的客户ID(crm.db)')
    converted_at = db.Column(db.DateTime, comment='转化时间')
    conversion_value = db.Column(db.Numeric(12, 2), comment='转化金额')
    
    # 积分记录（关联HR系统）
    points_earned = db.Column(db.Numeric(8, 2), default=0, comment='获得积分')
    
    # 跟进统计
    follow_count = db.Column(db.Integer, default=0, comment='跟进次数')
    last_follow_at = db.Column(db.DateTime, comment='最后跟进时间')
    next_follow_at = db.Column(db.DateTime, comment='下次跟进时间')
    
    # 标签
    tags = db.Column(db.JSON, default=list, comment='标签')
    priority = db.Column(db.Integer, default=3, comment='优先级 1-5')
    
    # 备注
    remark = db.Column(db.Text, comment='备注')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, comment='创建人')
    
    def to_dict(self, include_follows=False):
        data = {
            'id': self.id,
            'lead_no': self.lead_no,
            'name': self.name,
            'phone': self.phone,
            'phone_secondary': self.phone_secondary,
            'wechat': self.wechat,
            'building_name': self.building_name,
            'house_type': self.house_type,
            'area': float(self.area) if self.area else None,
            'budget': float(self.budget) if self.budget else None,
            'style_preference': self.style_preference,
            'status': self.status,
            'source_channel': self.source_channel,
            'source_detail': self.source_detail,
            'assigned_to': self.assigned_to,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'converted_to_customer_id': self.converted_to_customer_id,
            'converted_at': self.converted_at.isoformat() if self.converted_at else None,
            'conversion_value': float(self.conversion_value) if self.conversion_value else None,
            'points_earned': float(self.points_earned),
            'follow_count': self.follow_count,
            'last_follow_at': self.last_follow_at.isoformat() if self.last_follow_at else None,
            'next_follow_at': self.next_follow_at.isoformat() if self.next_follow_at else None,
            'tags': self.tags or [],
            'priority': self.priority,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        return data


class LeadFollow(db.Model):
    """线索跟进记录"""
    __tablename__ = 'lead_follow'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)
    
    # 跟进信息
    follow_type = db.Column(db.String(20), comment='phone/wechat/visit/other')
    content = db.Column(db.Text, nullable=False, comment='跟进内容')
    
    # 客户反馈
    customer_feedback = db.Column(db.Text, comment='客户反馈')
    interest_level = db.Column(db.String(10), comment='兴趣度:high/medium/low')
    
    # 下次跟进
    next_follow_type = db.Column(db.String(20), comment='下次跟进方式')
    next_follow_at = db.Column(db.DateTime, comment='下次跟进时间')
    
    # 关联信息
    appointment_booked = db.Column(db.Boolean, default=False, comment='是否预约到店')
    appointment_date = db.Column(db.Date, comment='预约日期')
    
    # 积分
    points_earned = db.Column(db.Numeric(6, 2), default=0, comment='本次跟进获得积分')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, comment='跟进人')
    
    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'follow_type': self.follow_type,
            'content': self.content,
            'customer_feedback': self.customer_feedback,
            'interest_level': self.interest_level,
            'next_follow_at': self.next_follow_at.isoformat() if self.next_follow_at else None,
            'appointment_booked': self.appointment_booked,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'points_earned': float(self.points_earned),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PublicSeaLead(db.Model):
    """公海线索"""
    __tablename__ = 'public_sea_lead'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False, unique=True)
    
    # 入池信息
    entered_at = db.Column(db.DateTime, default=datetime.utcnow, comment='入池时间')
    entered_reason = db.Column(db.String(50), comment='入池原因:unfollowed/returned/expired')
    
    # 保护期
    protected_by = db.Column(db.Integer, comment='被谁领取')
    protected_at = db.Column(db.DateTime, comment='领取时间')
    protect_expire_at = db.Column(db.DateTime, comment='保护期过期时间')
    
    # 领取限制
    max_claims = db.Column(db.Integer, default=3, comment='最大领取次数')
    claim_count = db.Column(db.Integer, default=0, comment='已被领取次数')
    
    status = db.Column(db.String(20), default='available', comment='available/protected/claimed')
    
    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'entered_at': self.entered_at.isoformat() if self.entered_at else None,
            'entered_reason': self.entered_reason,
            'protected_by': self.protected_by,
            'protected_at': self.protected_at.isoformat() if self.protected_at else None,
            'protect_expire_at': self.protect_expire_at.isoformat() if self.protect_expire_at else None,
            'claim_count': self.claim_count,
            'status': self.status
        }


class LeadDistributionLog(db.Model):
    """线索分配记录"""
    __tablename__ = 'lead_distribution_log'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)
    
    # 分配信息
    from_employee_id = db.Column(db.Integer, comment='原负责人')
    to_employee_id = db.Column(db.Integer, nullable=False, comment='新负责人')
    distributed_by = db.Column(db.Integer, comment='分配人')
    distributed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 分配原因
    reason = db.Column(db.String(200), comment='分配原因')
    distribution_type = db.Column(db.String(20), default='manual', comment='manual/auto/transfer')
    
    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'from_employee_id': self.from_employee_id,
            'to_employee_id': self.to_employee_id,
            'distributed_at': self.distributed_at.isoformat() if self.distributed_at else None,
            'reason': self.reason,
            'distribution_type': self.distribution_type
        }


class LeadChannelStats(db.Model):
    """线索渠道统计"""
    __tablename__ = 'lead_channel_stats'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    stat_date = db.Column(db.Date, nullable=False, comment='统计日期')
    channel = db.Column(db.String(50), nullable=False, comment='渠道名称')
    
    # 数量统计
    new_count = db.Column(db.Integer, default=0, comment='新增线索')
    assigned_count = db.Column(db.Integer, default=0, comment='分配线索')
    followed_count = db.Column(db.Integer, default=0, comment='跟进线索')
    appointment_count = db.Column(db.Integer, default=0, comment='预约数')
    visit_count = db.Column(db.Integer, default=0, comment='到店数')
    quote_count = db.Column(db.Integer, default=0, comment='报价数')
    deposit_count = db.Column(db.Integer, default=0, comment='定金数')
    converted_count = db.Column(db.Integer, default=0, comment='转化数')
    invalid_count = db.Column(db.Integer, default=0, comment='无效数')
    
    # 金额统计
    total_budget = db.Column(db.Numeric(14, 2), default=0, comment='总预算')
    total_conversion = db.Column(db.Numeric(14, 2), default=0, comment='总转化金额')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'stat_date': self.stat_date.isoformat() if self.stat_date else None,
            'channel': self.channel,
            'new_count': self.new_count,
            'assigned_count': self.assigned_count,
            'followed_count': self.followed_count,
            'appointment_count': self.appointment_count,
            'visit_count': self.visit_count,
            'quote_count': self.quote_count,
            'deposit_count': self.deposit_count,
            'converted_count': self.converted_count,
            'invalid_count': self.invalid_count,
            'conversion_rate': round(self.converted_count / self.new_count * 100, 2) if self.new_count else 0
        }
