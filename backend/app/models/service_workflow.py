"""
服务流程模块 - 58节点全案服务流程
V3.0 全新设计
"""
from datetime import datetime
from app import db


class WorkflowNode(db.Model):
    """流程节点定义"""
    __tablename__ = 'workflow_node'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 节点标识
    node_code = db.Column(db.String(20), unique=True, nullable=False, comment='节点编码如 N01')
    node_name = db.Column(db.String(100), nullable=False, comment='节点名称')

    # 阶段归属
    phase = db.Column(db.String(50), nullable=False, comment='阶段')
    phase_order = db.Column(db.Integer, default=0, comment='阶段内顺序')

    # 节点详情
    description = db.Column(db.Text, comment='节点描述')
    responsible_roles = db.Column(db.JSON, default=list, comment='负责角色')
    # 示例: ["销售", "规划师"]

    # 输入输出
    input_requirements = db.Column(db.JSON, default=list, comment='输入要求')
    output_deliverables = db.Column(db.JSON, default=list, comment='交付物')

    # 关联模块
    related_module = db.Column(db.String(50), comment='关联模块')
    # customer/material/finance/quote 等

    # 财务联动
    finance_trigger = db.Column(db.Boolean, default=False, comment='是否触发财务')
    finance_type = db.Column(db.String(50), comment='财务类型')
    # deposit/progress/final/quality/after_sales

    # 状态
    is_enabled = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'node_code': self.node_code,
            'node_name': self.node_name,
            'phase': self.phase,
            'phase_order': self.phase_order,
            'description': self.description,
            'responsible_roles': self.responsible_roles or [],
            'input_requirements': self.input_requirements or [],
            'output_deliverables': self.output_deliverables or [],
            'related_module': self.related_module,
            'finance_trigger': self.finance_trigger,
            'finance_type': self.finance_type,
            'is_enabled': self.is_enabled,
        }


class CustomerWorkflow(db.Model):
    """客户流程实例"""
    __tablename__ = 'customer_workflow'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), default='0', index=True)

    # 关联
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    contract_id = db.Column(db.Integer, comment='关联合同ID')

    # 流程状态
    current_node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id'), comment='当前节点')
    current_phase = db.Column(db.String(50), comment='当前阶段')
    status = db.Column(db.String(20), default='active', comment='流程状态')
    # active/paused/completed/cancelled

    # 时间
    start_date = db.Column(db.Date, comment='开工日期')
    planned_end_date = db.Column(db.Date, comment='计划完工日期')
    actual_end_date = db.Column(db.Date, comment='实际完工日期')

    # 统计
    total_nodes = db.Column(db.Integer, default=58, comment='总节点数')
    completed_nodes = db.Column(db.Integer, default=0, comment='已完成节点数')

    case_id = db.Column(db.Integer, db.ForeignKey('case_study.id'), comment='关联案例ID')
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    customer = db.relationship('Customer', lazy='joined')
    current_node = db.relationship('WorkflowNode', lazy='joined')
    node_records = db.relationship('WorkflowNodeRecord', backref='workflow', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_records=False):
        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'case_id': self.case_id,
            'customer_name': self.customer.name if self.customer else None,
            'contract_id': self.contract_id,
            'current_node_id': self.current_node_id,
            'current_node_name': self.current_node.node_name if self.current_node else None,
            'current_node_code': self.current_node.node_code if self.current_node else None,
            'current_phase': self.current_phase,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'planned_end_date': self.planned_end_date.isoformat() if self.planned_end_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'progress': {
                'total': self.total_nodes,
                'completed': self.completed_nodes,
                'percentage': round(self.completed_nodes / self.total_nodes * 100, 1) if self.total_nodes else 0
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_records:
            data['node_records'] = [r.to_dict() for r in self.node_records.order_by(WorkflowNodeRecord.created_at.desc())]
        return data


class WorkflowNodeRecord(db.Model):
    """节点执行记录"""
    __tablename__ = 'workflow_node_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 关联
    workflow_id = db.Column(db.Integer, db.ForeignKey('customer_workflow.id'), nullable=False)
    node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id'), nullable=False)

    # 执行信息
    status = db.Column(db.String(20), default='pending', comment='状态')
    # pending/processing/completed/skipped

    # 负责人
    assigned_to = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='指派给')
    executed_by = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='实际执行人')

    # 时间
    assigned_at = db.Column(db.DateTime, comment='指派时间')
    started_at = db.Column(db.DateTime, comment='开始时间')
    completed_at = db.Column(db.DateTime, comment='完成时间')
    deadline = db.Column(db.DateTime, comment='截止时间')

    # 内容
    content = db.Column(db.Text, comment='执行内容/汇报')
    attachments = db.Column(db.JSON, default=list, comment='附件')
    # [{name, url, type}]

    # 关联数据
    related_data = db.Column(db.JSON, default=dict, comment='关联数据')
    # 根据节点类型存储不同数据
    # 如: {"survey_id": 123, "quote_id": 456}

    # 备注
    remark = db.Column(db.Text, comment='备注')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    node = db.relationship('WorkflowNode', lazy='joined')
    assignee = db.relationship('Employee', foreign_keys=[assigned_to], lazy='joined')
    executor = db.relationship('Employee', foreign_keys=[executed_by], lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'node_id': self.node_id,
            'node_name': self.node.node_name if self.node else None,
            'node_code': self.node.node_code if self.node else None,
            'phase': self.node.phase if self.node else None,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'assigned_name': self.assignee.name if self.assignee else None,
            'executed_by': self.executed_by,
            'executor_name': self.executor.name if self.executor else None,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'content': self.content,
            'attachments': self.attachments or [],
            'related_data': self.related_data or {},
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class WorkflowPhaseConfig(db.Model):
    """阶段配置 - 支持自定义名称和排序"""
    __tablename__ = 'workflow_phase_config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False, comment='阶段编码')
    name = db.Column(db.String(100), nullable=False, comment='阶段显示名称')
    color = db.Column(db.String(20), default='#1890FF', comment='主题色')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    tenant_id = db.Column(db.String(32), default='0', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        # 统计该阶段下的节点数
        node_count = WorkflowNode.query.filter_by(
            phase=self.code, is_enabled=True
        ).count()
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'color': self.color,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'node_count': node_count,
        }


# 默认阶段定义（用于首次初始化）
DEFAULT_PHASES = [
    {'code': 'acquisition', 'name': '获客沉淀', 'color': '#1890FF', 'sort_order': 1},
    {'code': 'conversion', 'name': '转化签约', 'color': '#52C41A', 'sort_order': 2},
    {'code': 'preparation', 'name': '前期准备', 'color': '#722ED1', 'sort_order': 3},
    {'code': 'construction', 'name': '硬装施工', 'color': '#FA8C16', 'sort_order': 4},
    {'code': 'soft_service', 'name': '软装交付', 'color': '#13C2C2', 'sort_order': 5},
    {'code': 'after_sales', 'name': '售后服务', 'color': '#EB2F96', 'sort_order': 6},
]

# 兼容旧代码的 PHASES 别名（运行时应从数据库读取）
PHASES = [
    {'code': 'acquisition', 'name': '获客沉淀', 'color': '#1890FF'},
    {'code': 'conversion', 'name': '转化签约', 'color': '#52C41A'},
    {'code': 'preparation', 'name': '前期准备', 'color': '#722ED1'},
    {'code': 'construction', 'name': '硬装施工', 'color': '#FA8C16'},
    {'code': 'soft_service', 'name': '软装交付', 'color': '#13C2C2'},
    {'code': 'after_sales', 'name': '售后服务', 'color': '#EB2F96'},
]

# 58节点完整定义（用于初始化）
NODES_DEFINITION = [
    # 获客沉淀阶段 (1-8)
    {'code': 'N01', 'name': '多渠道获客', 'phase': 'acquisition', 'roles': ['运营', '销售'], 'module': 'customer'},
    {'code': 'N02', 'name': '客户初步筛选', 'phase': 'acquisition', 'roles': ['销售'], 'module': 'customer'},
    {'code': 'N03', 'name': '首次沟通', 'phase': 'acquisition', 'roles': ['销售'], 'module': 'customer'},
    {'code': 'N04', 'name': '楼盘调查', 'phase': 'acquisition', 'roles': ['销售', '规划师'], 'module': 'customer'},
    {'code': 'N05', 'name': '楼盘合作推进', 'phase': 'acquisition', 'roles': ['运营', '店长'], 'module': 'customer'},
    {'code': 'N06', 'name': '客户激活跟进', 'phase': 'acquisition', 'roles': ['销售'], 'module': 'customer'},
    {'code': 'N07', 'name': '首次量尺', 'phase': 'acquisition', 'roles': ['规划师', '设计师'], 'module': 'customer'},
    {'code': 'N08', 'name': '客户信息完善', 'phase': 'acquisition', 'roles': ['规划师'], 'module': 'customer'},

    # 转化签约阶段 (9-18)
    {'code': 'N09', 'name': '制作提案PPT', 'phase': 'conversion', 'roles': ['全案规划师'], 'module': 'quote'},
    {'code': 'N10', 'name': '提案汇报演示', 'phase': 'conversion', 'roles': ['规划师', '销售'], 'module': 'quote'},
    {'code': 'N11', 'name': '收取设计定金', 'phase': 'conversion', 'roles': ['销售'], 'module': 'finance', 'finance': 'deposit'},
    {'code': 'N12', 'name': '效果图设计', 'phase': 'conversion', 'roles': ['设计师'], 'module': 'quote'},
    {'code': 'N13', 'name': '预算拆解', 'phase': 'conversion', 'roles': ['预算专员'], 'module': 'quote'},
    {'code': 'N14', 'name': '效果图汇报确认', 'phase': 'conversion', 'roles': ['设计师', '规划师'], 'module': 'quote'},
    {'code': 'N15', 'name': '预算汇报沟通', 'phase': 'conversion', 'roles': ['设计师', '规划师'], 'module': 'quote'},
    {'code': 'N16', 'name': '客户正式认可', 'phase': 'conversion', 'roles': ['规划师', '商务'], 'module': 'quote'},
    {'code': 'N17', 'name': '合同拟定审核', 'phase': 'conversion', 'roles': ['规划师', '商务'], 'module': 'contract'},
    {'code': 'N18', 'name': '签合同+收首付款', 'phase': 'conversion', 'roles': ['商务', '财务'], 'module': 'finance', 'finance': 'first_payment'},

    # 前期准备阶段 (19-21)
    {'code': 'N19', 'name': '开工前复尺', 'phase': 'preparation', 'roles': ['施工图设计师', '施工负责人'], 'module': 'customer'},
    {'code': 'N20', 'name': '深化设计出图', 'phase': 'preparation', 'roles': ['设计师'], 'module': 'customer'},
    {'code': 'N21', 'name': '物料备料规划', 'phase': 'preparation', 'roles': ['商务', '施工负责人'], 'module': 'material'},

    # 硬装施工阶段 (22-43)
    {'code': 'N22', 'name': '开工仪式', 'phase': 'construction', 'roles': ['销售', '施工'], 'module': 'customer'},
    {'code': 'N23', 'name': '现场保护', 'phase': 'construction', 'roles': ['施工负责人'], 'module': 'customer'},
    {'code': 'N24', 'name': '墙体拆改', 'phase': 'construction', 'roles': ['施工负责人'], 'module': 'customer'},
    {'code': 'N25', 'name': '水电开槽', 'phase': 'construction', 'roles': ['水电师傅'], 'module': 'customer'},
    {'code': 'N26', 'name': '水电布管穿线', 'phase': 'construction', 'roles': ['水电师傅'], 'module': 'customer'},
    {'code': 'N27', 'name': '水电封槽', 'phase': 'construction', 'roles': ['施工负责人'], 'module': 'customer'},
    {'code': 'N28', 'name': '暖通隐蔽工程', 'phase': 'construction', 'roles': ['暖通师傅'], 'module': 'customer'},
    {'code': 'N29', 'name': '木工吊顶/造型', 'phase': 'construction', 'roles': ['木工师傅'], 'module': 'customer'},
    {'code': 'N30', 'name': '墙固地固', 'phase': 'construction', 'roles': ['施工负责人'], 'module': 'customer'},
    {'code': 'N31', 'name': '砌墙/抹灰', 'phase': 'construction', 'roles': ['瓦工师傅'], 'module': 'customer'},
    {'code': 'N32', 'name': '防水施工', 'phase': 'construction', 'roles': ['防水师傅'], 'module': 'customer'},
    {'code': 'N33', 'name': '防水保护层', 'phase': 'construction', 'roles': ['瓦工师傅'], 'module': 'customer'},
    {'code': 'N34', 'name': '地砖铺贴', 'phase': 'construction', 'roles': ['瓦工师傅'], 'module': 'customer'},
    {'code': 'N35', 'name': '墙砖铺贴', 'phase': 'construction', 'roles': ['瓦工师傅'], 'module': 'customer'},
    {'code': 'N36', 'name': '地面找平', 'phase': 'construction', 'roles': ['瓦工师傅'], 'module': 'customer'},
    {'code': 'N37', 'name': '室内木作安装', 'phase': 'construction', 'roles': ['木工师傅'], 'module': 'customer'},
    {'code': 'N38', 'name': '油工基层处理', 'phase': 'construction', 'roles': ['油工师傅'], 'module': 'customer'},
    {'code': 'N39', 'name': '底漆涂刷', 'phase': 'construction', 'roles': ['油工师傅'], 'module': 'customer'},
    {'code': 'N40', 'name': '面漆涂刷/喷涂', 'phase': 'construction', 'roles': ['油工师傅'], 'module': 'customer'},
    {'code': 'N41', 'name': '硬装开荒保洁', 'phase': 'construction', 'roles': ['施工负责人'], 'module': 'customer'},
    {'code': 'N42', 'name': '硬装中期验收', 'phase': 'construction', 'roles': ['监理', '客户'], 'module': 'customer'},
    {'code': 'N43', 'name': '硬装竣工验收', 'phase': 'construction', 'roles': ['监理', '客户', '总部'], 'module': 'customer'},

    # 软装交付阶段 (44-53)
    {'code': 'N44', 'name': '进度款收取', 'phase': 'soft_service', 'roles': ['财务', '销售'], 'module': 'finance', 'finance': 'progress'},
    {'code': 'N45', 'name': '定制/家具下单', 'phase': 'soft_service', 'roles': ['物料专员'], 'module': 'material'},
    {'code': 'N46', 'name': '物料入库验收', 'phase': 'soft_service', 'roles': ['物料专员'], 'module': 'material'},
    {'code': 'N47', 'name': '尾款验证冲账', 'phase': 'soft_service', 'roles': ['财务', '物料'], 'module': 'finance', 'finance': 'final'},
    {'code': 'N48', 'name': '软装出库配送', 'phase': 'soft_service', 'roles': ['物料专员'], 'module': 'material'},
    {'code': 'N49', 'name': '家具/软装安装', 'phase': 'soft_service', 'roles': ['安装师傅'], 'module': 'customer'},
    {'code': 'N50', 'name': '调试检测', 'phase': 'soft_service', 'roles': ['安装师傅'], 'module': 'customer'},
    {'code': 'N51', 'name': '软装分项验收', 'phase': 'soft_service', 'roles': ['监理', '客户'], 'module': 'customer'},
    {'code': 'N52', 'name': '全屋整体验收', 'phase': 'soft_service', 'roles': ['规划师', '监理', '客户'], 'module': 'customer'},
    {'code': 'N53', 'name': '交付资料移交', 'phase': 'soft_service', 'roles': ['销售'], 'module': 'customer'},

    # 售后服务阶段 (54-58)
    {'code': 'N54', 'name': '售后工单处理', 'phase': 'after_sales', 'roles': ['售后专员'], 'module': 'customer'},
    {'code': 'N55', 'name': '客户档案归档', 'phase': 'after_sales', 'roles': ['客服'], 'module': 'customer'},
    {'code': 'N56', 'name': '生长动画+相册制作', 'phase': 'after_sales', 'roles': ['全案设计师', '规划师'], 'module': 'customer'},
    {'code': 'N57', 'name': '家访准备与上门', 'phase': 'after_sales', 'roles': ['规划师', '店长'], 'module': 'customer'},
    {'code': 'N58', 'name': '总结复盘', 'phase': 'after_sales', 'roles': ['团队'], 'module': 'customer'},
]
