"""
人力资源管理系统 V2.0 模型（最终整合版）

重要：Department/Position/Employee 已移至 hr.py，本文件仅保留扩展模型。
所有表均在主数据库（无 __bind_key__）。
"""
from datetime import datetime
from app import db


class EmployeeSalary(db.Model):
    """员工薪酬记录"""
    __tablename__ = 'employee_salary'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    # 薪资期间
    year = db.Column(db.Integer, nullable=False, comment='年份')
    month = db.Column(db.Integer, nullable=False, comment='月份')

    # 基本工资结构
    base_salary = db.Column(db.Numeric(10, 2), default=0, comment='基本工资')
    position_allowance = db.Column(db.Numeric(10, 2), default=0, comment='岗位津贴')
    performance_allowance = db.Column(db.Numeric(10, 2), default=0, comment='绩效津贴')
    seniority_allowance = db.Column(db.Numeric(10, 2), default=0, comment='工龄津贴')

    # 提成与奖金
    commission = db.Column(db.Numeric(10, 2), default=0, comment='销售提成')
    project_bonus = db.Column(db.Numeric(10, 2), default=0, comment='项目奖金')
    attendance_bonus = db.Column(db.Numeric(10, 2), default=0, comment='全勤奖')
    other_bonus = db.Column(db.Numeric(10, 2), default=0, comment='其他奖金')

    # 应发合计
    gross_salary = db.Column(db.Numeric(10, 2), default=0, comment='应发工资')

    # 扣除项
    social_insurance = db.Column(db.Numeric(10, 2), default=0, comment='社保')
    housing_fund = db.Column(db.Numeric(10, 2), default=0, comment='公积金')
    personal_tax = db.Column(db.Numeric(10, 2), default=0, comment='个人所得税')
    other_deduction = db.Column(db.Numeric(10, 2), default=0, comment='其他扣除')

    # 实发工资
    net_salary = db.Column(db.Numeric(10, 2), default=0, comment='实发工资')

    # 状态
    status = db.Column(db.String(20), default='draft', comment='draft/calculated/confirmed/paid')
    confirmed_at = db.Column(db.DateTime, comment='确认时间')
    confirmed_by = db.Column(db.Integer, comment='确认人')
    paid_at = db.Column(db.DateTime, comment='发放时间')

    remark = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'year': self.year,
            'month': self.month,
            'period': f"{self.year}-{str(self.month).zfill(2)}",
            'base_salary': float(self.base_salary),
            'position_allowance': float(self.position_allowance),
            'performance_allowance': float(self.performance_allowance),
            'seniority_allowance': float(self.seniority_allowance),
            'commission': float(self.commission),
            'project_bonus': float(self.project_bonus),
            'attendance_bonus': float(self.attendance_bonus),
            'other_bonus': float(self.other_bonus),
            'gross_salary': float(self.gross_salary),
            'social_insurance': float(self.social_insurance),
            'housing_fund': float(self.housing_fund),
            'personal_tax': float(self.personal_tax),
            'other_deduction': float(self.other_deduction),
            'net_salary': float(self.net_salary),
            'status': self.status,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }

    def calculate_gross(self):
        self.gross_salary = (
            self.base_salary + self.position_allowance +
            self.performance_allowance + self.seniority_allowance +
            self.commission + self.project_bonus +
            self.attendance_bonus + self.other_bonus
        )
        return self.gross_salary

    def calculate_net(self):
        self.calculate_gross()
        self.net_salary = (
            self.gross_salary - self.social_insurance -
            self.housing_fund - self.personal_tax - self.other_deduction
        )
        return self.net_salary


class PerformanceReview(db.Model):
    """绩效考核"""
    __tablename__ = 'performance_review'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    # 考核周期
    review_year = db.Column(db.Integer, nullable=False)
    review_quarter = db.Column(db.Integer, comment='季度 1-4，为空表示年度考核')
    review_type = db.Column(db.String(20), default='quarterly', comment='monthly/quarterly/annual')

    # 考核维度
    kpi_score = db.Column(db.Numeric(4, 2), default=0, comment='KPI得分 0-100')
    ability_score = db.Column(db.Numeric(4, 2), default=0, comment='能力得分')
    attitude_score = db.Column(db.Numeric(4, 2), default=0, comment='态度得分')
    total_score = db.Column(db.Numeric(4, 2), default=0, comment='总分')

    # 评级
    grade = db.Column(db.String(10), comment='等级:S/A/B/C/D')

    # 评语
    self_review = db.Column(db.Text, comment='自评')
    manager_review = db.Column(db.Text, comment='上级评价')
    improvement_plan = db.Column(db.Text, comment='改进计划')

    # 流程
    reviewer_id = db.Column(db.Integer, comment='考核人')
    review_date = db.Column(db.Date, comment='考核日期')
    status = db.Column(db.String(20), default='pending', comment='pending/self_reviewed/manager_reviewed/confirmed')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'review_year': self.review_year,
            'review_quarter': self.review_quarter,
            'period': f"{self.review_year}Q{self.review_quarter}" if self.review_quarter else str(self.review_year),
            'review_type': self.review_type,
            'kpi_score': float(self.kpi_score),
            'ability_score': float(self.ability_score),
            'attitude_score': float(self.attitude_score),
            'total_score': float(self.total_score),
            'grade': self.grade,
            'self_review': self.self_review,
            'manager_review': self.manager_review,
            'improvement_plan': self.improvement_plan,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            'status': self.status
        }

    def calculate_total(self):
        weights = {'kpi': 0.6, 'ability': 0.2, 'attitude': 0.2}
        self.total_score = (
            self.kpi_score * weights['kpi'] +
            self.ability_score * weights['ability'] +
            self.attitude_score * weights['attitude']
        )
        if self.total_score >= 95:
            self.grade = 'S'
        elif self.total_score >= 85:
            self.grade = 'A'
        elif self.total_score >= 75:
            self.grade = 'B'
        elif self.total_score >= 60:
            self.grade = 'C'
        else:
            self.grade = 'D'
        return self.total_score


class EmployeePoints(db.Model):
    """员工积分账户"""
    __tablename__ = 'employee_points'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, unique=True)

    current_points = db.Column(db.Numeric(10, 2), default=0, comment='当前积分')
    total_earned = db.Column(db.Numeric(10, 2), default=0, comment='累计获得')
    total_used = db.Column(db.Numeric(10, 2), default=0, comment='累计使用')

    level = db.Column(db.Integer, default=1, comment='积分等级')
    level_name = db.Column(db.String(20), default='青铜', comment='等级名称')

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'current_points': float(self.current_points),
            'total_earned': float(self.total_earned),
            'total_used': float(self.total_used),
            'level': self.level,
            'level_name': self.level_name
        }

    def update_level(self):
        points = float(self.current_points)
        levels = [(0, 1, '青铜'), (100, 2, '白银'), (300, 3, '黄金'),
                  (600, 4, '铂金'), (1000, 5, '钻石'), (2000, 6, '星耀')]
        for threshold, level, name in reversed(levels):
            if points >= threshold:
                self.level = level
                self.level_name = name
                break


class PointsTransaction(db.Model):
    """积分流水"""
    __tablename__ = 'points_transaction'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    type = db.Column(db.String(20), nullable=False, comment='earn/use/expire/adjust')
    points = db.Column(db.Numeric(8, 2), nullable=False, comment='积分变动(正数增加)')
    balance_after = db.Column(db.Numeric(10, 2), comment='变动后余额')

    source_type = db.Column(db.String(50), comment='来源类型:lead/customer/contract/manual')
    source_id = db.Column(db.Integer, comment='来源记录ID')
    description = db.Column(db.String(200), comment='描述')

    related_lead_id = db.Column(db.Integer, comment='关联线索ID')
    related_customer_id = db.Column(db.Integer, comment='关联客户ID')
    related_contract_id = db.Column(db.Integer, comment='关联合同ID')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, comment='操作人')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'type': self.type,
            'points': float(self.points),
            'balance_after': float(self.balance_after) if self.balance_after else None,
            'source_type': self.source_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CareerPath(db.Model):
    """职业发展路径"""
    __tablename__ = 'career_path'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    current_level = db.Column(db.Integer, comment='当前职级')
    target_level = db.Column(db.Integer, comment='目标职级')

    path_type = db.Column(db.String(20), comment='management/expert/sales')

    current_skills = db.Column(db.JSON, default=list, comment='当前技能')
    target_skills = db.Column(db.JSON, default=list, comment='目标技能')
    skill_gaps = db.Column(db.JSON, default=list, comment='技能差距')

    short_term_goals = db.Column(db.Text, comment='短期目标(3-6月)')
    mid_term_goals = db.Column(db.Text, comment='中期目标(6-12月)')
    long_term_goals = db.Column(db.Text, comment='长期目标(1-3年)')

    training_plan = db.Column(db.JSON, default=list, comment='培训计划')

    mentor_id = db.Column(db.Integer, comment='导师ID')

    status = db.Column(db.String(20), default='active', comment='active/completed/paused')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'current_level': self.current_level,
            'target_level': self.target_level,
            'path_type': self.path_type,
            'current_skills': self.current_skills or [],
            'target_skills': self.target_skills or [],
            'skill_gaps': self.skill_gaps or [],
            'short_term_goals': self.short_term_goals,
            'mid_term_goals': self.mid_term_goals,
            'long_term_goals': self.long_term_goals,
            'training_plan': self.training_plan or [],
            'mentor_id': self.mentor_id,
            'status': self.status
        }


class TrainingRecord(db.Model):
    """培训记录"""
    __tablename__ = 'training_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    training_name = db.Column(db.String(100), nullable=False, comment='培训名称')
    training_type = db.Column(db.String(20), comment='内部/外部/在线')
    provider = db.Column(db.String(100), comment='培训机构')

    start_date = db.Column(db.Date, comment='开始日期')
    end_date = db.Column(db.Date, comment='结束日期')
    duration_hours = db.Column(db.Integer, comment='培训时长(小时)')

    completion_status = db.Column(db.String(20), default='completed', comment='completed/incomplete')
    score = db.Column(db.Numeric(4, 2), comment='成绩')
    certificate = db.Column(db.String(200), comment='证书编号/文件')

    feedback = db.Column(db.Text, comment='培训反馈')
    application_plan = db.Column(db.Text, comment='应用计划')

    cost = db.Column(db.Numeric(10, 2), comment='培训费用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'training_name': self.training_name,
            'training_type': self.training_type,
            'provider': self.provider,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration_hours': self.duration_hours,
            'completion_status': self.completion_status,
            'score': float(self.score) if self.score else None,
            'certificate': self.certificate,
            'cost': float(self.cost) if self.cost else None
        }


class EmployeeWelfare(db.Model):
    """员工福利记录"""
    __tablename__ = 'employee_welfare'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    welfare_type = db.Column(db.String(30), nullable=False, comment='类型')
    title = db.Column(db.String(100), comment='福利标题')
    description = db.Column(db.Text, comment='福利描述')
    benefit_value = db.Column(db.Numeric(10, 2), comment='福利价值')

    event_date = db.Column(db.Date, comment='福利事件日期')
    granted_at = db.Column(db.DateTime, default=datetime.utcnow, comment='发放时间')

    status = db.Column(db.String(20), default='granted', comment='granted/received')

    remark = db.Column(db.Text, comment='备注')
    created_by = db.Column(db.Integer, comment='创建人')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'welfare_type': self.welfare_type,
            'title': self.title,
            'description': self.description,
            'benefit_value': float(self.benefit_value) if self.benefit_value else None,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
            'status': self.status
        }
"""
人力资源 V2 扩展模型 - 积分系统升级（2026-05-06）
基于 hr_v2.py 末尾追加，不修改已有模型
"""

class PointsRule(db.Model):
    """积分规则配置"""
    __tablename__ = 'points_rule'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 归属
    tenant_id = db.Column(db.String(50), default='default', comment='租户ID')

    # 规则基本信息
    action_key = db.Column(db.String(50), unique=True, nullable=False, comment='动作唯一标识')
    action_name = db.Column(db.String(100), nullable=False, comment='动作名称')
    category = db.Column(db.String(30), nullable=False, comment='获客/转化/成交/施工/售后')
    description = db.Column(db.String(200), comment='规则说明')

    # 积分配置
    points = db.Column(db.Integer, nullable=False, default=0, comment='基础积分')
    points_type = db.Column(db.String(20), default='earn', comment='earn获取/use消费/exchange兑换')
    unit = db.Column(db.String(20), default='次', comment='单位：次/条/人/单')

    # 高客单叠加（成交类专有）
    high_value_enabled = db.Column(db.Boolean, default=False, comment='是否启用高客单叠加')
    thresholds = db.Column(db.JSON, default=list, comment='高客单阈值配置 [{"min":50000,"max":100000,"bonus":300}]')

    # 状态
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    is_auditable = db.Column(db.Boolean, default=True, comment='是否需审核')
    requires_proof = db.Column(db.Boolean, default=False, comment='是否需上传凭证')

    # 关联（灵活关联到任意业务表）
    related_table = db.Column(db.String(50), comment='关联业务表:leads/customers/contracts等')
    related_action = db.Column(db.String(50), comment='关联动作:created/updated/paid等')

    # 可选：指定哪些角色可执行此动作获得积分
    allowed_roles = db.Column(db.JSON, default=list, comment='允许执行的角色列表')
    excluded_roles = db.Column(db.JSON, default=list, comment='排除的角色列表')

    created_by = db.Column(db.Integer, comment='创建人')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'action_key': self.action_key,
            'action_name': self.action_name,
            'category': self.category,
            'description': self.description,
            'points': self.points,
            'points_type': self.points_type,
            'unit': self.unit,
            'high_value_enabled': self.high_value_enabled,
            'thresholds': self.thresholds or [],
            'is_active': self.is_active,
            'is_auditable': self.is_auditable,
            'requires_proof': self.requires_proof,
            'related_table': self.related_table,
            'related_action': self.related_action,
            'allowed_roles': self.allowed_roles or [],
            'excluded_roles': self.excluded_roles or [],
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PointsAudit(db.Model):
    """积分审核记录"""
    __tablename__ = 'points_audit'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 申请人
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    employee_name = db.Column(db.String(50), comment='申请人姓名(冗余)')

    # 申请信息
    action_key = db.Column(db.String(50), nullable=False, comment='动作标识')
    action_name = db.Column(db.String(100), nullable=False, comment='动作名称')
    category = db.Column(db.String(30), comment='分类')
    points_applied = db.Column(db.Integer, nullable=False, comment='申请积分')
    proof_url = db.Column(db.String(500), comment='凭证URL')
    remark = db.Column(db.Text, comment='申请备注')

    # 关联业务
    related_table = db.Column(db.String(50), comment='关联表')
    related_id = db.Column(db.Integer, comment='关联记录ID')

    # 审核
    status = db.Column(db.String(20), default='pending', comment='pending待审核/approved已通过/rejected已驳回/cancelled已取消')
    audited_by = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='审核人')
    audited_by_name = db.Column(db.String(50), comment='审核人姓名')
    audited_at = db.Column(db.DateTime, comment='审核时间')
    reject_reason = db.Column(db.String(200), comment='驳回原因')

    # 积分是否已发放
    points_granted = db.Column(db.Boolean, default=False, comment='积分是否已发放')
    points_granted_at = db.Column(db.DateTime, comment='积分发放时间')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'action_key': self.action_key,
            'action_name': self.action_name,
            'category': self.category,
            'points_applied': self.points_applied,
            'proof_url': self.proof_url,
            'remark': self.remark,
            'related_table': self.related_table,
            'related_id': self.related_id,
            'status': self.status,
            'audited_by': self.audited_by,
            'audited_by_name': self.audited_by_name,
            'audited_at': self.audited_at.isoformat() if self.audited_at else None,
            'reject_reason': self.reject_reason,
            'points_granted': self.points_granted,
            'points_granted_at': self.points_granted_at.isoformat() if self.points_granted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TeamBuilding(db.Model):
    """团队团建申请"""
    __tablename__ = 'team_building'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 基本信息
    tenant_id = db.Column(db.String(50), default='default', comment='租户ID')
    team_name = db.Column(db.String(100), nullable=False, comment='团队名称')
    leader_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False, comment='负责人')
    leader_name = db.Column(db.String(50), comment='负责人姓名')
    member_count = db.Column(db.Integer, nullable=False, comment='团队人数')

    # 积分计算
    total_points_required = db.Column(db.Integer, nullable=False, comment='所需总积分')
    fund_amount = db.Column(db.Numeric(10, 2), nullable=False, comment='团建基金')
    max_reimbursement = db.Column(db.Numeric(10, 2), nullable=False, comment='最高可报销')
    actual_cost = db.Column(db.Numeric(10, 2), default=0, comment='实际花费')
    status = db.Column(db.String(20), default='voting', comment='voting投票中/pending待审核/approved已通过/rejected已驳回/completed已完成/rejected_reimburse报销拒绝')

    # 成员投票
    member_list = db.Column(db.JSON, default=list, comment='全体成员列表 [{"id":1,"name":"张三"}]')
    member_agree = db.Column(db.JSON, default=list, comment='同意成员ID列表')
    member_refuse = db.Column(db.JSON, default=list, comment='拒绝成员ID列表')
    is_incomplete = db.Column(db.Boolean, default=False, comment='团队不完整标记')

    # 积分扣除（审核通过后填写）
    deduction_list = db.Column(db.JSON, default=list, comment='每人扣积分明细 [{"employee_id":1,"name":"张三","points":5000}]')

    # 团建资料（完成后上传）
    video_url = db.Column(db.String(500), comment='视频链接')
    image_urls = db.Column(db.JSON, default=list, comment='现场照片列表')
    bill_urls = db.Column(db.JSON, default=list, comment='消费清单+发票')
    evaluation_stats = db.Column(db.JSON, default=dict, comment='匿名评价统计 {"satisfied":8,"neutral":1,"unsatisfied":0}')

    # 报销
    reimbursement_status = db.Column(db.String(20), default='none', comment='none未申请/pending待审核/approved已报销/rejected已拒绝')
    reimbursement_amount = db.Column(db.Numeric(10, 2), default=0, comment='实报金额')
    reimbursement_remark = db.Column(db.String(200), comment='报销备注')

    # 不满意处理
    unsatisfied_count = db.Column(db.Integer, default=0, comment='不满意人数')

    # 审核
    approved_by = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='审核人')
    approved_by_name = db.Column(db.String(50), comment='审核人姓名')
    approved_at = db.Column(db.DateTime, comment='审核时间')
    reject_reason = db.Column(db.String(200), comment='驳回原因')

    # 评分（完成后）
    team_rating = db.Column(db.Numeric(2, 1), comment='团队评分1-5')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'team_name': self.team_name,
            'leader_id': self.leader_id,
            'leader_name': self.leader_name,
            'member_count': self.member_count,
            'total_points_required': self.total_points_required,
            'fund_amount': float(self.fund_amount),
            'max_reimbursement': float(self.max_reimbursement),
            'actual_cost': float(self.actual_cost),
            'status': self.status,
            'member_list': self.member_list or [],
            'member_agree': self.member_agree or [],
            'member_refuse': self.member_refuse or [],
            'is_incomplete': self.is_incomplete,
            'deduction_list': self.deduction_list or [],
            'video_url': self.video_url,
            'image_urls': self.image_urls or [],
            'bill_urls': self.bill_urls or [],
            'evaluation_stats': self.evaluation_stats or {},
            'reimbursement_status': self.reimbursement_status,
            'reimbursement_amount': float(self.reimbursement_amount) if self.reimbursement_amount else 0,
            'reimbursement_remark': self.reimbursement_remark,
            'unsatisfied_count': self.unsatisfied_count,
            'approved_by': self.approved_by,
            'approved_by_name': self.approved_by_name,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'reject_reason': self.reject_reason,
            'team_rating': float(self.team_rating) if self.team_rating else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PointsExchange(db.Model):
    """积分兑换记录（现金/假期）"""
    __tablename__ = 'points_exchange'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    employee_name = db.Column(db.String(50), comment='员工姓名')

    exchange_type = db.Column(db.String(20), nullable=False, comment='cash现金/leave带薪假')

    # 现金兑换
    points_spent = db.Column(db.Integer, nullable=False, comment='消耗积分')
    cash_amount = db.Column(db.Numeric(10, 2), comment='兑换现金金额')
    exchange_rate = db.Column(db.Numeric(6, 2), comment='兑换比例')

    # 带薪假兑换
    days_off = db.Column(db.Integer, comment='兑换天数')
    points_required_per_day = db.Column(db.Integer, default=2000, comment='每天所需积分')
    yearly_limit_used = db.Column(db.Integer, default=0, comment='年内已用次数')

    status = db.Column(db.String(20), default='approved', comment='pending/approved/rejected')
    audited_by = db.Column(db.Integer, comment='审核人')
    audited_at = db.Column(db.DateTime, comment='审核时间')
    reject_reason = db.Column(db.String(200), comment='驳回原因')

    remark = db.Column(db.String(200), comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'exchange_type': self.exchange_type,
            'points_spent': self.points_spent,
            'cash_amount': float(self.cash_amount) if self.cash_amount else None,
            'exchange_rate': float(self.exchange_rate) if self.exchange_rate else None,
            'days_off': self.days_off,
            'points_required_per_day': self.points_required_per_day,
            'yearly_limit_used': self.yearly_limit_used,
            'status': self.status,
            'audited_by': self.audited_by,
            'audited_at': self.audited_at.isoformat() if self.audited_at else None,
            'reject_reason': self.reject_reason,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
