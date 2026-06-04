"""
留资引导模块数据模型 V2.0 - 多分店客资线索管理系统
支持积分激励、公海机制、转化漏斗
"""

from datetime import datetime
from app import db


class Lead(db.Model):
    """留资线索表 V2.0"""
    __tablename__ = 'lead'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # ========== 基础信息 ==========
    name = db.Column(db.String(50), comment='客户姓名')
    phone = db.Column(db.String(20), unique=True, nullable=False, comment='手机号')
    wechat = db.Column(db.String(50), comment='微信号')
    gender = db.Column(db.String(10), comment='性别')
    
    # ========== 来源信息 ==========
    source = db.Column(db.String(50), comment='来源渠道')
    source_id = db.Column(db.Integer, comment='来源关联ID')
    source_page = db.Column(db.String(200), comment='来源页面URL')
    source_detail = db.Column(db.String(100), comment='来源详情')
    
    # ========== 楼盘信息（升级客户必填） ==========
    building_name = db.Column(db.String(100), comment='楼盘名称')
    building_address = db.Column(db.String(200), comment='详细地址')
    house_type = db.Column(db.String(50), comment='户型')
    area = db.Column(db.Float, comment='面积')
    floor = db.Column(db.String(20), comment='楼层')
    delivery_date = db.Column(db.Date, comment='交房时间')
    decoration_status = db.Column(db.String(50), comment='装修状态')
    
    # ========== 需求信息 ==========
    decoration_type = db.Column(db.String(50), comment='装修类型')
    style_preference = db.Column(db.String(100), comment='风格偏好')
    budget = db.Column(db.String(50), comment='预算范围')
    timeline = db.Column(db.String(50), comment='工期要求')
    detailed_needs = db.Column(db.Text, comment='详细需求')
    family_structure = db.Column(db.String(200), comment='家庭结构')
    living_habits = db.Column(db.String(500), comment='生活习惯')
    hobbies = db.Column(db.String(200), comment='爱好')
    special_requirements = db.Column(db.String(500), comment='特殊要求')
    focus_points = db.Column(db.String(500), comment='关注点')
    
    # ========== 标签体系 ==========
    tags = db.Column(db.JSON, comment='标签数组')
    
    # ========== 转化状态 ==========
    status = db.Column(db.String(20), default='待分配', comment='转化状态')
    intention_level = db.Column(db.String(20), default='中', comment='意向等级')
    conversion_level = db.Column(db.String(20), default='线索', comment='转化等级')
    
    # ========== 分配信息 ==========
    assigned_to = db.Column(db.Integer, comment='负责人ID(employee表)')
    assigned_at = db.Column(db.DateTime, comment='分配时间')
    assigned_by = db.Column(db.Integer, comment='分配人ID')
    
    # ========== 跟进信息 ==========
    follow_count = db.Column(db.Integer, default=0, comment='跟进次数')
    first_contact_at = db.Column(db.DateTime, comment='首次联系时间')
    last_follow_at = db.Column(db.DateTime, comment='最后跟进时间')
    next_follow_at = db.Column(db.DateTime, comment='下次跟进时间')
    is_overdue = db.Column(db.Boolean, default=False, comment='是否逾期')
    overdue_days = db.Column(db.Integer, default=0, comment='逾期天数')
    
    # ========== 到店信息 ==========
    is_visited = db.Column(db.Boolean, default=False, comment='是否到店')
    visited_at = db.Column(db.DateTime, comment='到店时间')
    is_measured = db.Column(db.Boolean, default=False, comment='是否量房')
    measured_at = db.Column(db.DateTime, comment='量房时间')
    
    # ========== 方案信息 ==========
    has_scheme = db.Column(db.Boolean, default=False, comment='是否出方案')
    scheme_at = db.Column(db.DateTime, comment='出方案时间')
    
    # ========== 成交信息 ==========
    deposit_amount = db.Column(db.Numeric(12, 2), comment='定金金额')
    deposit_at = db.Column(db.DateTime, comment='交定金时间')
    contract_type = db.Column(db.String(50), comment='签约类型')
    contract_amount = db.Column(db.Numeric(12, 2), comment='签约金额')
    contract_at = db.Column(db.DateTime, comment='签约时间')
    deal_at = db.Column(db.DateTime, comment='成交时间')
    
    # ========== 公海信息 ==========
    is_in_sea = db.Column(db.Boolean, default=False, comment='是否在公海')
    sea_at = db.Column(db.DateTime, comment='入公海时间')
    sea_reason = db.Column(db.String(100), comment='入公海原因')
    sea_retrieved_by = db.Column(db.Integer, comment='领取人ID')
    sea_retrieved_at = db.Column(db.DateTime, comment='领取时间')
    
    # ========== 积分信息 ==========
    total_points = db.Column(db.Integer, default=0, comment='总积分贡献')
    
    # ========== 其他 ==========
    remark = db.Column(db.Text, comment='备注')
    is_invalid = db.Column(db.Boolean, default=False, comment='是否标记无效')
    invalid_reason = db.Column(db.String(200), comment='无效原因')
    ip_address = db.Column(db.String(50), comment='访客IP')
    appointment_id = db.Column(db.Integer, comment='关联预约ID')
    user_agent = db.Column(db.Text, comment='访客UA')
    tenant_id = db.Column(db.String(20), comment='租户ID')
    created_by = db.Column(db.Integer, comment='录入人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ========== 关联关系 ==========
    # Note: follows/points relationships removed due to cross-database issues
    # Use LeadFollow.query.filter_by(lead_id=...) and LeadPoint.query.filter_by(lead_id=...) instead
    # employee = db.relationship('Employee', backref='leads', lazy='joined')

    # ========== 状态常量 ==========
    STATUS_PENDING = '待分配'
    STATUS_ASSIGNED = '已分配'
    STATUS_FOLLOWING = '跟进中'
    STATUS_VISITED = '已到店'
    STATUS_MEASURED = '已量房'
    STATUS_SCHEMED = '已出方案'
    STATUS_DEPOSIT = '已交定金'
    STATUS_CONTRACTED = '已签约'
    STATUS_DEAL = '已成交'
    STATUS_INVALID = '无效'
    STATUS_SEA = '公海'

    # 意向等级
    INTENTION_HIGH = '高'
    INTENTION_MEDIUM = '中'
    INTENTION_LOW = '低'
    INTENTION_INVALID = '无效'

    # 转化等级
    LEVEL_LEAD = '线索'
    LEVEL_CUSTOMER = '客户'
    LEVEL_VIP = 'VIP'
    LEVEL_SVIP = 'SVIP'

    # 来源渠道
    SOURCES = [
        '案例留资', '快速咨询', '预约量房', '楼盘调研',
        '异业合作', '小红书', '公众号', '抖音',
        '短视频', '转介绍', '线下活动', '其他'
    ]

    def to_dict(self, include_follows=False, include_points=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'wechat': self.wechat,
            'gender': self.gender,
            'source': self.source,
            'source_detail': self.source_detail,
            'building_name': self.building_name,
            'building_address': self.building_address,
            'house_type': self.house_type,
            'area': float(self.area) if self.area else None,
            'floor': self.floor,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'decoration_status': self.decoration_status,
            'decoration_type': self.decoration_type,
            'style_preference': self.style_preference,
            'budget': self.budget,
            'timeline': self.timeline,
            'detailed_needs': self.detailed_needs,
            'family_structure': self.family_structure,
            'living_habits': self.living_habits,
            'hobbies': self.hobbies,
            'special_requirements': self.special_requirements,
            'focus_points': self.focus_points,
            'tags': self.tags or [],
            'status': self.status,
            'intention_level': self.intention_level,
            'conversion_level': self.conversion_level,
            'assigned_to': self.assigned_to,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'follow_count': self.follow_count,
            'first_contact_at': self.first_contact_at.isoformat() if self.first_contact_at else None,
            'last_follow_at': self.last_follow_at.isoformat() if self.last_follow_at else None,
            'next_follow_at': self.next_follow_at.isoformat() if self.next_follow_at else None,
            'is_overdue': self.is_overdue,
            'overdue_days': self.overdue_days,
            'is_visited': self.is_visited,
            'visited_at': self.visited_at.isoformat() if self.visited_at else None,
            'is_measured': self.is_measured,
            'measured_at': self.measured_at.isoformat() if self.measured_at else None,
            'has_scheme': self.has_scheme,
            'scheme_at': self.scheme_at.isoformat() if self.scheme_at else None,
            'deposit_amount': float(self.deposit_amount) if self.deposit_amount else None,
            'deposit_at': self.deposit_at.isoformat() if self.deposit_at else None,
            'contract_type': self.contract_type,
            'contract_amount': float(self.contract_amount) if self.contract_amount else None,
            'contract_at': self.contract_at.isoformat() if self.contract_at else None,
            'deal_at': self.deal_at.isoformat() if self.deal_at else None,
            'is_in_sea': self.is_in_sea,
            'sea_at': self.sea_at.isoformat() if self.sea_at else None,
            'sea_reason': self.sea_reason,
            'total_points': self.total_points,
            'remark': self.remark,
            'is_invalid': self.is_invalid,
            'invalid_reason': self.invalid_reason,
            'appointment_id': self.appointment_id,
            'ip_address': self.ip_address,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_follows:
            # Query follows directly instead of using relationship
            follows = LeadFollow.query.filter_by(lead_id=self.id).order_by(LeadFollow.created_at.desc()).all()
            data['follows'] = [f.to_dict() for f in follows]
        
        if include_points:
            # Query points directly instead of using relationship
            points = LeadPoint.query.filter_by(lead_id=self.id).order_by(LeadPoint.created_at.desc()).all()
            data['points'] = [p.to_dict() for p in points]

        return data

    def can_upgrade_to_customer(self):
        """检查是否可以升级为客户"""
        return all([
            self.name,
            self.phone,
            self.building_name,
            self.building_address,
            self.detailed_needs
        ])

    def upgrade_to_customer(self):
        """升级为客户"""
        if self.can_upgrade_to_customer():
            self.conversion_level = self.LEVEL_CUSTOMER
            db.session.commit()
            return True
        return False

    def assign_to(self, employee_id, assigned_by=None):
        """分配给指定员工"""
        self.assigned_to = employee_id
        self.assigned_at = datetime.utcnow()
        self.assigned_by = assigned_by
        self.status = self.STATUS_FOLLOWING
        self.is_in_sea = False
        db.session.commit()

    def move_to_sea(self, reason='逾期未跟进'):
        """移入公海"""
        self.is_in_sea = True
        self.sea_at = datetime.utcnow()
        self.sea_reason = reason
        self.status = self.STATUS_SEA
        self.assigned_to = None
        db.session.commit()

    def retrieve_from_sea(self, employee_id):
        """从公海领取"""
        self.is_in_sea = False
        self.sea_retrieved_by = employee_id
        self.sea_retrieved_at = datetime.utcnow()
        self.assign_to(employee_id)
        db.session.commit()

    def update_status(self, status):
        """更新状态"""
        self.status = status
        
        if status == self.STATUS_CONTACTED and not self.first_contact_at:
            self.first_contact_at = datetime.utcnow()
        elif status == self.STATUS_VISITED:
            self.is_visited = True
            self.visited_at = datetime.utcnow()
        elif status == self.STATUS_MEASURED:
            self.is_measured = True
            self.measured_at = datetime.utcnow()
        elif status == self.STATUS_SCHEMED:
            self.has_scheme = True
            self.scheme_at = datetime.utcnow()
        elif status == self.STATUS_DEPOSIT:
            self.conversion_level = self.LEVEL_VIP
        elif status == self.STATUS_DEAL:
            self.deal_at = datetime.utcnow()
            self.conversion_level = self.LEVEL_VIP
        
        db.session.commit()

    def add_follow(self, follow_type, content, next_follow_at=None, operator_id=None):
        """添加跟进记录"""
        follow = LeadFollow(
            lead_id=self.id,
            follow_type=follow_type,
            content=content,
            next_follow_at=next_follow_at,
            operator_id=operator_id
        )
        db.session.add(follow)
        self.follow_count += 1
        self.last_follow_at = datetime.utcnow()
        self.next_follow_at = next_follow_at
        
        # 更新逾期状态
        if next_follow_at:
            self.is_overdue = False
            self.overdue_days = 0
        
        db.session.commit()
        return follow

    def check_overdue(self):
        """检查是否逾期"""
        if self.next_follow_at and self.next_follow_at < datetime.utcnow():
            self.is_overdue = True
            self.overdue_days = (datetime.utcnow() - self.next_follow_at).days
            
            # 7天未跟进自动入公海
            if self.overdue_days >= 7 and not self.is_in_sea:
                self.move_to_sea('逾期7天未跟进')
            
            db.session.commit()
        return self.is_overdue


class LeadFollow(db.Model):
    """线索跟进记录表 V2.0"""
    __tablename__ = 'lead_follow'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)
    follow_type = db.Column(db.String(20), comment='跟进方式')
    content = db.Column(db.Text, comment='跟进内容')
    result = db.Column(db.String(100), comment='跟进结果')
    next_follow_at = db.Column(db.DateTime, comment='下次跟进时间')
    is_visited = db.Column(db.Boolean, default=False, comment='是否预约到店')
    visited_at = db.Column(db.DateTime, comment='预约到店时间')
    attachments = db.Column(db.JSON, comment='附件数组')
    operator_id = db.Column(db.Integer, comment='操作人ID(employee表)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联（跨数据库，注释掉relationship）
    # operator = db.relationship('Employee', backref='lead_follows', lazy='joined')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'follow_type': self.follow_type,
            'content': self.content,
            'result': self.result,
            'next_follow_at': self.next_follow_at.isoformat() if self.next_follow_at else None,
            'is_visited': self.is_visited,
            'visited_at': self.visited_at.isoformat() if self.visited_at else None,
            'attachments': self.attachments or [],
            'operator_id': self.operator_id,
            'operator_name': None,  # Cross-db relationship removed
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class LeadPoint(db.Model):
    """线索积分记录表"""
    __tablename__ = 'lead_point'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)
    employee_id = db.Column(db.Integer, nullable=False, comment='获得积分的员工ID(employee表)')
    point_type = db.Column(db.String(50), nullable=False, comment='积分类型')
    points = db.Column(db.Integer, nullable=False, comment='积分值')
    description = db.Column(db.String(200), comment='积分说明')
    related_follow_id = db.Column(db.Integer, comment='关联跟进记录ID(lead_follow表)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联（跨数据库关系注释掉）
    # employee = db.relationship('Employee', backref='lead_points', lazy='joined')
    # follow = db.relationship('LeadFollow', backref='points', lazy='joined')

    # 积分类型常量
    TYPE_CREATE = '录入线索'
    TYPE_FOLLOW = '有效跟进'
    TYPE_APPOINT_VISIT = '预约到店'
    TYPE_ACTUAL_VISIT = '实际到店'
    TYPE_GET_NEEDS = '获取需求'
    TYPE_DEPOSIT = '交定金'
    TYPE_CONTRACT_FULL = '签约全案'
    TYPE_CONTRACT_HARD = '签约硬装施工'
    TYPE_CONTRACT_MATERIAL = '签约硬装主材'
    TYPE_CONTRACT_CUSTOM = '签约全屋定制'
    TYPE_CONTRACT_FURNITURE = '签约成品家具'
    TYPE_CONTRACT_SOFT = '签约软装饰品'
    TYPE_PUNISH_OVERDUE = '逾期扣分'
    TYPE_PUNISH_FAKE = '虚假信息'
    TYPE_PUNISH_ABANDON = '恶意放弃'

    POINT_RULES = {
        TYPE_CREATE: 1,
        TYPE_FOLLOW: 1,
        TYPE_APPOINT_VISIT: 0.5,
        TYPE_ACTUAL_VISIT: 2,
        TYPE_GET_NEEDS: 1,
        TYPE_DEPOSIT: 10,
        TYPE_CONTRACT_FULL: 60,
        TYPE_CONTRACT_HARD: 10,
        TYPE_CONTRACT_MATERIAL: 20,
        TYPE_CONTRACT_CUSTOM: 10,
        TYPE_CONTRACT_FURNITURE: 15,
        TYPE_CONTRACT_SOFT: 15,
        TYPE_PUNISH_OVERDUE: -1,
        TYPE_PUNISH_FAKE: -5,
        TYPE_PUNISH_ABANDON: -10,
    }

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'employee_id': self.employee_id,
            'employee_name': None,  # Cross-db relationship removed
            'point_type': self.point_type,
            'points': self.points,
            'description': self.description,
            'related_follow_id': self.related_follow_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def add_points(cls, lead_id, employee_id, point_type, description=None, follow_id=None):
        """添加积分记录"""
        points = cls.POINT_RULES.get(point_type, 0)
        
        record = cls(
            lead_id=lead_id,
            employee_id=employee_id,
            point_type=point_type,
            points=points,
            description=description or point_type,
            related_follow_id=follow_id
        )
        db.session.add(record)
        
        # 更新线索总积分
        lead = Lead.query.get(lead_id)
        if lead:
            lead.total_points += points
        
        db.session.commit()
        return record


class LeadDistribution(db.Model):
    """线索分配记录表"""
    __tablename__ = 'lead_distribution'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)
    from_employee_id = db.Column(db.Integer, comment='原负责人ID')
    to_employee_id = db.Column(db.Integer, nullable=False, comment='新负责人ID(employee表)')
    distributed_by = db.Column(db.Integer, comment='分配人ID')
    distribution_type = db.Column(db.String(20), comment='分配类型：手动/自动/领取')
    reason = db.Column(db.String(200), comment='分配原因')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联（跨数据库关系注释掉）
    lead = db.relationship('Lead', backref='distributions', lazy='joined')
    # to_employee = db.relationship('Employee', backref='received_leads', lazy='joined')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'lead_name': self.lead.name if self.lead else None,
            'from_employee_id': self.from_employee_id,
            'to_employee_id': self.to_employee_id,
            'to_employee_name': None,  # 跨数据库，需单独查询
            'distributed_by': self.distributed_by,
            'distribution_type': self.distribution_type,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class LeadChannelStat(db.Model):
    """线索渠道统计表（每日汇总）"""
    __tablename__ = 'lead_channel_stat'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stat_date = db.Column(db.Date, nullable=False, comment='统计日期')
    channel = db.Column(db.String(50), nullable=False, comment='渠道名称')
    lead_count = db.Column(db.Integer, default=0, comment='线索数')
    valid_count = db.Column(db.Integer, default=0, comment='有效数')
    follow_count = db.Column(db.Integer, default=0, comment='跟进数')
    visit_count = db.Column(db.Integer, default=0, comment='到店数')
    deposit_count = db.Column(db.Integer, default=0, comment='定金数')
    contract_count = db.Column(db.Integer, default=0, comment='签约数')
    deal_amount = db.Column(db.Numeric(12, 2), default=0, comment='成交金额')
    cost = db.Column(db.Numeric(12, 2), default=0, comment='投放成本')
    tenant_id = db.Column(db.String(20), comment='租户ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """转换为字典"""
        conversion_rate = round(self.contract_count / self.lead_count * 100, 2) if self.lead_count > 0 else 0
        return {
            'id': self.id,
            'stat_date': self.stat_date.isoformat() if self.stat_date else None,
            'channel': self.channel,
            'lead_count': self.lead_count,
            'valid_count': self.valid_count,
            'follow_count': self.follow_count,
            'visit_count': self.visit_count,
            'deposit_count': self.deposit_count,
            'contract_count': self.contract_count,
            'deal_amount': float(self.deal_amount) if self.deal_amount else 0,
            'cost': float(self.cost) if self.cost else 0,
            'conversion_rate': conversion_rate,
            'roi': round(float(self.deal_amount) / float(self.cost), 2) if self.cost and float(self.cost) > 0 else 0,
        }
