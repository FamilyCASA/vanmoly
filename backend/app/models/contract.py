"""
合同管理模块 - 数据模型
V3.0 全新设计
"""
from datetime import datetime
from app import db


class ContractTemplate(db.Model):
    """合同模板"""
    __tablename__ = 'contract_template'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    name = db.Column(db.String(100), nullable=False, comment='模板名称')
    code = db.Column(db.String(50), comment='模板编码')
    contract_type = db.Column(db.String(50), comment='合同类型')
    # design(设计合同)/construction(施工合同)/all_in(全案合同)/soft(软装合同)

    content = db.Column(db.Text, comment='模板内容')
    variables = db.Column(db.JSON, default=list, comment='变量定义')
    # [{name, label, type, required}]

    is_default = db.Column(db.Boolean, default=False, comment='是否默认')
    is_enabled = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    remark = db.Column(db.String(500), default='', comment='备注')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'contract_type': self.contract_type,
            'content': self.content,
            'variables': self.variables or [],
            'is_default': self.is_default,
            'is_enabled': self.is_enabled,
            'remark': self.remark or '',
        }


class Contract(db.Model):
    """合同表"""
    __tablename__ = 'contract'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    # 合同编号
    contract_no = db.Column(db.String(50), unique=True, nullable=False, comment='合同编号')

    # 关联
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False, comment='客户')
    template_id = db.Column(db.Integer, db.ForeignKey('contract_template.id'), comment='使用模板')
    workflow_id = db.Column(db.Integer, comment='关联流程')

    # 合同类型
    contract_type = db.Column(db.String(50), comment='合同类型')
    # design/construction/all_in/soft

    # 合同金额
    total_amount = db.Column(db.Numeric(12, 2), default=0, comment='合同总金额')
    design_fee = db.Column(db.Numeric(10, 2), default=0, comment='设计费')
    construction_fee = db.Column(db.Numeric(12, 2), default=0, comment='施工费')
    material_fee = db.Column(db.Numeric(12, 2), default=0, comment='材料费')
    soft_fee = db.Column(db.Numeric(12, 2), default=0, comment='软装费')

    # 付款计划
    payment_schedule = db.Column(db.JSON, default=list, comment='付款计划')
    # [
    #   {phase: '定金', percentage: 10, amount: 10000, status: 'paid/pending'},
    #   {phase: '首付款', percentage: 30, amount: 30000, status: 'pending'},
    #   ...
    # ]

    # 合同期限
    start_date = db.Column(db.Date, comment='开始日期')
    end_date = db.Column(db.Date, comment='结束日期')
    signed_date = db.Column(db.Date, comment='签署日期')

    # 合同内容
    title = db.Column(db.String(200), comment='合同标题')
    content = db.Column(db.Text, comment='合同正文')
    variables = db.Column(db.JSON, default=dict, comment='变量值')

    # 附件
    attachments = db.Column(db.JSON, default=list, comment='附件')
    # [{name, url, type}]

    # 签署信息
    signed_by_customer = db.Column(db.Boolean, default=False, comment='客户已签')
    signed_by_company = db.Column(db.Boolean, default=False, comment='公司已签')
    customer_sign_date = db.Column(db.DateTime, comment='客户签署时间')
    company_sign_date = db.Column(db.DateTime, comment='公司签署时间')

    # 状态
    status = db.Column(db.String(20), default='draft', comment='状态')
    # draft(草稿)/pending(待签署)/signed(已签署)/executing(执行中)/completed(已完成)/cancelled(已取消)

    # 负责人
    creator_id = db.Column(db.Integer, comment='创建人')
    manager_id = db.Column(db.Integer, comment='合同负责人')

    remark = db.Column(db.Text, comment='备注')
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'contract_no': self.contract_no,
            'customer_id': self.customer_id,
            'contract_type': self.contract_type,
            'title': self.title,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'design_fee': float(self.design_fee) if self.design_fee else 0,
            'construction_fee': float(self.construction_fee) if self.construction_fee else 0,
            'material_fee': float(self.material_fee) if self.material_fee else 0,
            'soft_fee': float(self.soft_fee) if self.soft_fee else 0,
            'payment_schedule': self.payment_schedule or [],
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'signed_date': self.signed_date.isoformat() if self.signed_date else None,
            'signed_by_customer': self.signed_by_customer,
            'signed_by_company': self.signed_by_company,
            'status': self.status,
            'creator_id': self.creator_id,
            'manager_id': self.manager_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

        if include_content:
            data['content'] = self.content
            data['variables'] = self.variables or {}
            data['attachments'] = self.attachments or []

        return data


class ContractPayment(db.Model):
    """合同付款记录"""
    __tablename__ = 'contract_payment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)

    # 付款信息
    phase = db.Column(db.String(50), comment='付款阶段')
    phase_name = db.Column(db.String(100), comment='阶段名称')
    node_desc = db.Column(db.String(200), comment='节点说明')
    # deposit(定金)/first(首付款)/progress(进度款)/final(尾款)/quality(质保金)

    percentage = db.Column(db.Numeric(5, 2), comment='占比%')
    amount = db.Column(db.Numeric(12, 2), comment='金额')

    # 付款状态
    status = db.Column(db.String(20), default='pending', comment='状态')
    # pending(待付)/paid(已付)/overdue(逾期)

    planned_date = db.Column(db.Date, comment='计划付款日期')
    actual_date = db.Column(db.Date, comment='实际付款日期')

    # 收款信息
    payment_method = db.Column(db.String(50), comment='付款方式')
    # cash/transfer/alipay/wechat

    transaction_no = db.Column(db.String(100), comment='交易流水号')
    receipt_url = db.Column(db.String(255), comment='收据/凭证')

    remark = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'phase': self.phase,
            'phase_name': self.phase_name or '',
            'node_desc': self.node_desc or '',
            'percentage': float(self.percentage) if self.percentage else 0,
            'amount': float(self.amount) if self.amount else 0,
            'status': self.status,
            'planned_date': self.planned_date.isoformat() if self.planned_date else None,
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'payment_method': self.payment_method,
            'transaction_no': self.transaction_no,
        }


class ContractChange(db.Model):
    """合同变更记录"""
    __tablename__ = 'contract_change'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)

    change_type = db.Column(db.String(50), comment='变更类型')
    # amount(金额变更)/date(日期变更)/content(内容变更)/cancel(取消)

    old_value = db.Column(db.JSON, comment='原值')
    new_value = db.Column(db.JSON, comment='新值')

    reason = db.Column(db.Text, comment='变更原因')
    attachments = db.Column(db.JSON, default=list, comment='附件')

    operator_id = db.Column(db.Integer, comment='操作人')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'change_type': self.change_type,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'reason': self.reason,
            'operator_id': self.operator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# 合同类型选项
CONTRACT_TYPES = [
    ('design', '设计合同'),
    ('construction', '施工合同'),
    ('all_in', '全案合同'),
    ('soft', '软装合同'),
    ('custom', '定制合同'),
]

# 合同状态选项
CONTRACT_STATUS = [
    ('draft', '草稿'),
    ('pending', '待签署'),
    ('signed', '已签署'),
    ('executing', '执行中'),
    ('completed', '已完成'),
    ('cancelled', '已取消'),
]

# 付款阶段
PAYMENT_PHASES = [
    ('deposit', '定金'),
    ('first', '首付款'),
    ('progress', '进度款'),
    ('final', '尾款'),
    ('quality', '质保金'),
]
