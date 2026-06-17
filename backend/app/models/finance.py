# -*- coding: utf-8 -*-
"""
财务管理模块 - V3.0

包含：
- 组织架构与权限（finance_role, finance_member, finance_approval_flow）
- 删除申请管理（finance_delete_request）
- 流水管理（finance_transaction, finance_category）
- 报销管理（finance_reimbursement）
- 投资管理（finance_shareholder, finance_charter）
- 操作日志（finance_audit_log）

所有表都在主数据库（无 __bind_key__）。
不使用跨库外键约束，仅保留同库内的外键。
"""
from datetime import datetime
from app import db
import json


class FinanceRole(db.Model):
    """财务角色配置"""
    __tablename__ = 'finance_role'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    role_code = db.Column(db.String(50), unique=True, nullable=False, comment='角色标识')
    role_name = db.Column(db.String(50), nullable=False, comment='角色显示名称')
    permissions = db.Column(db.Text, comment='JSON数组，权限列表')
    can_delete = db.Column(db.Boolean, default=False, comment='是否可直接删除')
    delete_approval_required = db.Column(db.Boolean, default=True, comment='删除是否需要审批')
    description = db.Column(db.Text, comment='角色说明')
    is_system = db.Column(db.Boolean, default=False, comment='是否系统内置角色')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'role_code': self.role_code,
            'role_name': self.role_name,
            'permissions': json.loads(self.permissions) if self.permissions else [],
            'can_delete': self.can_delete,
            'delete_approval_required': self.delete_approval_required,
            'description': self.description,
            'is_system': self.is_system,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class FinanceMember(db.Model):
    """财务团队成员"""
    __tablename__ = 'finance_member'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    employee_id = db.Column(db.Integer, unique=True, nullable=False, comment='员工ID')
    role_id = db.Column(db.Integer, db.ForeignKey('finance_role.id'), nullable=False)
    delete_unlock_until = db.Column(db.DateTime, comment='删除解锁截止时间')
    is_active = db.Column(db.Boolean, default=True, comment='是否在职/启用')
    assigned_by = db.Column(db.Integer, comment='授权人')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    role = db.relationship('FinanceRole', backref='members')

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'employee_id': self.employee_id,
            'role_id': self.role_id,
            'role_name': self.role.role_name if self.role else None,
            'role_code': self.role.role_code if self.role else None,
            'delete_unlock_until': self.delete_unlock_until.isoformat() if self.delete_unlock_until else None,
            'is_active': self.is_active,
            'assigned_by': self.assigned_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class FinanceApprovalFlow(db.Model):
    """审批流程模板"""
    __tablename__ = 'finance_approval_flow'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    flow_name = db.Column(db.String(100), nullable=False, comment='流程名称')
    trigger_category_ids = db.Column(db.Text, comment='JSON数组，触发的分类ID范围')
    amount_threshold = db.Column(db.Numeric(12, 2), default=0, comment='金额门槛')
    steps = db.Column(db.Text, comment='JSON数组，审批步骤')
    is_default = db.Column(db.Boolean, default=False, comment='是否默认流程')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'flow_name': self.flow_name,
            'trigger_category_ids': json.loads(self.trigger_category_ids) if self.trigger_category_ids else [],
            'amount_threshold': float(self.amount_threshold) if self.amount_threshold else 0,
            'steps': json.loads(self.steps) if self.steps else [],
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class FinanceDeleteRequest(db.Model):
    """删除申请表"""
    __tablename__ = 'finance_delete_request'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    transaction_id = db.Column(db.Integer, db.ForeignKey('finance_transaction.id'), nullable=False)
    applicant_id = db.Column(db.Integer, nullable=False, comment='申请人ID')
    reason = db.Column(db.Text, nullable=False, comment='删除原因')
    status = db.Column(db.String(20), default='pending', comment='pending/approved/rejected')
    reviewed_by = db.Column(db.Integer, comment='审批人ID')
    reviewed_at = db.Column(db.DateTime)
    review_note = db.Column(db.Text, comment='审批意见')
    unlock_until = db.Column(db.DateTime, comment='删除解锁截止时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联（仅同库内）
    transaction = db.relationship('FinanceTransaction', backref='delete_requests')

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'transaction_id': self.transaction_id,
            'transaction_no': self.transaction.trans_no if self.transaction else None,
            'applicant_id': self.applicant_id,
            'reason': self.reason,
            'status': self.status,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_note': self.review_note,
            'unlock_until': self.unlock_until.isoformat() if self.unlock_until else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class FinanceTransaction(db.Model):
    """流水主表"""
    __tablename__ = 'finance_transaction'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    trans_no = db.Column(db.String(50), unique=True, nullable=False, comment='流水编号')
    trans_type = db.Column(db.String(20), nullable=False, comment='income/expense')
    trans_date = db.Column(db.Date, nullable=False, comment='发生日期')
    amount = db.Column(db.Numeric(12, 2), nullable=False, comment='金额')
    category_id = db.Column(db.Integer, db.ForeignKey('finance_category.id'))
    sub_category = db.Column(db.String(50), comment='子分类')
    summary = db.Column(db.String(200), comment='摘要/备注')

    # 关联字段（不使用外键约束，因为可能跨数据库）
    customer_id = db.Column(db.Integer, comment='客户ID')
    employee_id = db.Column(db.Integer, comment='员工ID')
    building_id = db.Column(db.Integer, comment='楼盘ID')
    case_study_id = db.Column(db.Integer, comment='案例ID')
    quote_id = db.Column(db.Integer, comment='报价单ID')
    contract_id = db.Column(db.Integer, comment='合同ID')
    material_sku_id = db.Column(db.Integer, comment='物料SKU ID')

    payment_method = db.Column(db.String(30), comment='支付方式')

    # 凭证（必填）
    voucher_files = db.Column(db.Text, comment='JSON数组，凭证文件列表')

    # 来源标记
    source_type = db.Column(db.String(20), default='manual', comment='manual/reimbursement/import')
    source_id = db.Column(db.Integer, comment='来源ID')

    # 删除标记
    deleted_at = db.Column(db.DateTime, comment='逻辑删除时间')
    deleted_by = db.Column(db.Integer, comment='删除人ID')
    delete_reason = db.Column(db.Text, comment='删除原因')

    # 审核
    operator_id = db.Column(db.Integer, comment='登记人ID')
    reviewed_by = db.Column(db.Integer, comment='审核人ID')
    reviewed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending', comment='pending/approved/rejected/deleted')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联（仅同库内）
    category = db.relationship('FinanceCategory', backref='transactions')

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'trans_no': self.trans_no,
            'trans_type': self.trans_type,
            'trans_date': self.trans_date.isoformat() if self.trans_date else None,
            'amount': float(self.amount) if self.amount else 0,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'sub_category': self.sub_category,
            'summary': self.summary,
            'payment_method': self.payment_method,
            'voucher_files': json.loads(self.voucher_files) if self.voucher_files else [],
            'source_type': self.source_type,
            'source_id': self.source_id,
            'status': self.status,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'delete_reason': self.delete_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class FinanceCategory(db.Model):
    """收支分类字典"""
    __tablename__ = 'finance_category'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    name = db.Column(db.String(50), nullable=False, comment='分类名称')
    type = db.Column(db.String(20), nullable=False, comment='income/expense')
    parent_id = db.Column(db.Integer, db.ForeignKey('finance_category.id'))
    sort_order = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(50), comment='图标标识')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    parent = db.relationship('FinanceCategory', remote_side=[id], backref='children')

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'type': self.type,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'icon': self.icon,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class FinanceReimbursement(db.Model):
    """费用报销单"""
    __tablename__ = 'finance_reimbursement'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    reimb_no = db.Column(db.String(50), unique=True, nullable=False, comment='报销编号')
    applicant_id = db.Column(db.Integer, nullable=False, comment='申请人ID')
    dept_id = db.Column(db.Integer, comment='部门ID')
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    expense_date = db.Column(db.Date, comment='费用发生日期')
    category_id = db.Column(db.Integer, db.ForeignKey('finance_category.id'))
    summary = db.Column(db.String(200), comment='报销事由摘要')
    detail_items = db.Column(db.Text, comment='JSON数组，明细项')

    # 审批字段
    status = db.Column(db.String(20), default='draft', comment='draft/submitted/approved/rejected/paid/cancelled')
    current_step = db.Column(db.Integer, default=0)
    submit_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, comment='审核人ID')
    reviewed_at = db.Column(db.DateTime)
    review_note = db.Column(db.Text)

    # 付款字段
    paid_by = db.Column(db.Integer, comment='付款人ID')
    paid_at = db.Column(db.DateTime)
    payment_method = db.Column(db.String(30))
    payment_voucher = db.Column(db.String(200), comment='付款凭证截图路径')

    # 关联流水
    transaction_id = db.Column(db.Integer, db.ForeignKey('finance_transaction.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    transaction = db.relationship('FinanceTransaction', backref='reimbursement_source')
    category = db.relationship('FinanceCategory', backref='reimbursements')

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'reimb_no': self.reimb_no,
            'applicant_id': self.applicant_id,
            'dept_id': self.dept_id,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'summary': self.summary,
            'detail_items': json.loads(self.detail_items) if self.detail_items else [],
            'status': self.status,
            'current_step': self.current_step,
            'submit_at': self.submit_at.isoformat() if self.submit_at else None,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_note': self.review_note,
            'paid_by': self.paid_by,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'payment_method': self.payment_method,
            'payment_voucher': self.payment_voucher,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class FinanceShareholder(db.Model):
    """股东信息"""
    __tablename__ = 'finance_shareholder'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    name = db.Column(db.String(50), nullable=False, comment='股东姓名')
    id_card = db.Column(db.String(100), comment='身份证号（加密存储）')
    phone = db.Column(db.String(20), comment='联系电话')
    share_ratio = db.Column(db.Numeric(5, 2), comment='持股比例（%）')
    investment_amount = db.Column(db.Numeric(12, 2), comment='投资金额（元）')
    investment_date = db.Column(db.Date, comment='投资日期')
    role = db.Column(db.String(30), comment='角色：director/manager/silent_investor')
    status = db.Column(db.String(20), default='active', comment='active/exited/pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'phone': self.phone,
            'share_ratio': float(self.share_ratio) if self.share_ratio else 0,
            'investment_amount': float(self.investment_amount) if self.investment_amount else 0,
            'investment_date': self.investment_date.isoformat() if self.investment_date else None,
            'role': self.role,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class FinanceCharter(db.Model):
    """企业章程"""
    __tablename__ = 'finance_charter'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    title = db.Column(db.String(100), nullable=False, comment='章程标题')
    content = db.Column(db.Text, comment='章程内容（富文本）')
    version = db.Column(db.String(20), comment='版本号')
    file_path = db.Column(db.String(200), comment='附件路径（PDF等）')
    effective_date = db.Column(db.Date, comment='生效日期')
    created_by = db.Column(db.Integer, comment='创建人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'title': self.title,
            'content': self.content,
            'version': self.version,
            'file_path': self.file_path,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class FinanceAuditLog(db.Model):
    """操作日志（数据库备份）"""
    __tablename__ = 'finance_audit_log'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    operator_id = db.Column(db.Integer, nullable=False, comment='操作人ID')
    action = db.Column(db.String(30), nullable=False, comment='create/update/delete/approve/pay/export')
    target_type = db.Column(db.String(30), nullable=False, comment='transaction/category/reimbursement/shareholder')
    target_id = db.Column(db.Integer, nullable=False)
    detail_before = db.Column(db.Text, comment='操作前数据快照（JSON）')
    detail_after = db.Column(db.Text, comment='操作后数据快照（JSON）')
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'operator_id': self.operator_id,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'detail_before': json.loads(self.detail_before) if self.detail_before else None,
            'detail_after': json.loads(self.detail_after) if self.detail_after else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class FinanceReceivable(db.Model):
    """应收款项 - 客户欠我们的钱"""
    __tablename__ = 'finance_receivable'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    receivable_no = db.Column(db.String(50), unique=True, nullable=False, comment='应收编号')
    receivable_type = db.Column(db.String(30), nullable=False, comment='contract/installment/other')
    amount = db.Column(db.Numeric(12, 2), nullable=False, comment='应收金额')
    received_amount = db.Column(db.Numeric(12, 2), default=0, comment='已收金额')
    remaining_amount = db.Column(db.Numeric(12, 2), comment='剩余应收')

    # 关联（无外键约束，跨库）
    customer_id = db.Column(db.Integer, comment='客户ID')
    contract_id = db.Column(db.Integer, comment='合同ID')
    quote_id = db.Column(db.Integer, comment='报价单ID')
    building_id = db.Column(db.Integer, comment='楼盘ID')

    title = db.Column(db.String(200), comment='应收事由')
    due_date = db.Column(db.Date, comment='预计收款日期')
    status = db.Column(db.String(20), default='pending', comment='pending/partial/received/overdue/cancelled')
    remark = db.Column(db.Text, comment='备注')

    operator_id = db.Column(db.Integer, comment='登记人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'receivable_no': self.receivable_no,
            'receivable_type': self.receivable_type,
            'amount': float(self.amount) if self.amount else 0,
            'received_amount': float(self.received_amount) if self.received_amount else 0,
            'remaining_amount': float(self.remaining_amount) if self.remaining_amount else 0,
            'customer_id': self.customer_id,
            'contract_id': self.contract_id,
            'quote_id': self.quote_id,
            'building_id': self.building_id,
            'title': self.title,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'remark': self.remark,
            'operator_id': self.operator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class FinancePayable(db.Model):
    """应付款项 - 我们欠供应商的钱"""
    __tablename__ = 'finance_payable'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    payable_no = db.Column(db.String(50), unique=True, nullable=False, comment='应付编号')
    payable_type = db.Column(db.String(30), nullable=False, comment='supplier/subcontract/material/other')
    amount = db.Column(db.Numeric(12, 2), nullable=False, comment='应付金额')
    paid_amount = db.Column(db.Numeric(12, 2), default=0, comment='已付金额')
    remaining_amount = db.Column(db.Numeric(12, 2), comment='剩余应付')

    # 关联（无外键约束，跨库）
    supplier_name = db.Column(db.String(100), comment='供应商/收款方名称')
    contract_id = db.Column(db.Integer, comment='合同ID')
    quote_id = db.Column(db.Integer, comment='报价单ID')
    building_id = db.Column(db.Integer, comment='楼盘ID')

    title = db.Column(db.String(200), comment='应付事由')
    due_date = db.Column(db.Date, comment='预计付款日期')
    status = db.Column(db.String(20), default='pending', comment='pending/partial/paid/overdue/cancelled')
    remark = db.Column(db.Text, comment='备注')

    operator_id = db.Column(db.Integer, comment='登记人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'payable_no': self.payable_no,
            'payable_type': self.payable_type,
            'amount': float(self.amount) if self.amount else 0,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0,
            'remaining_amount': float(self.remaining_amount) if self.remaining_amount else 0,
            'supplier_name': self.supplier_name,
            'contract_id': self.contract_id,
            'quote_id': self.quote_id,
            'building_id': self.building_id,
            'title': self.title,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'remark': self.remark,
            'operator_id': self.operator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class FinancePaymentPlan(db.Model):
    """付款计划 - 分期收款/付款的日程表"""
    __tablename__ = 'finance_payment_plan'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    plan_no = db.Column(db.String(50), unique=True, nullable=False, comment='计划编号')
    plan_type = db.Column(db.String(20), nullable=False, comment='receivable/payable')
    parent_id = db.Column(db.Integer, nullable=False, comment='关联的 receivable_id 或 payable_id')
    installment_no = db.Column(db.Integer, nullable=False, comment='期数')
    amount = db.Column(db.Numeric(12, 2), nullable=False, comment='本期金额')
    paid_amount = db.Column(db.Numeric(12, 2), default=0, comment='已付/已收金额')
    due_date = db.Column(db.Date, comment='预计收/付款日期')
    actual_date = db.Column(db.Date, comment='实际收/付款日期')
    status = db.Column(db.String(20), default='pending', comment='pending/paid/partial/overdue/cancelled')
    remark = db.Column(db.Text, comment='备注')
    transaction_id = db.Column(db.Integer, comment='关联流水ID')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'plan_no': self.plan_no,
            'plan_type': self.plan_type,
            'parent_id': self.parent_id,
            'installment_no': self.installment_no,
            'amount': float(self.amount) if self.amount else 0,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'status': self.status,
            'remark': self.remark,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
