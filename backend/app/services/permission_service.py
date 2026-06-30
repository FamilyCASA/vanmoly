# -*- coding: utf-8 -*-
"""
细粒度权限注册、校验与授权边界
"""
from functools import wraps
from flask import jsonify

from app import db
from app.models.auth_v2 import UserV2
from app.models.hr import Employee, Department, Position
from app.models.permission import PermissionAssignment, PermissionAuditLog
from app.models.project_team import ProjectTeam, ProjectTeamMember


# ============================================================
# 隐式权限继承规则表
# ============================================================
# 规则：只要用户具备某种身份/职务/岗位，就自动获得对应权限，无需手动授权。
# 格式: { 'role_key': { 'permissions': [...], 'scope': 'store/project/global' } }
#
# 身份来源优先级（高→低）：
#   1. 系统角色 (UserV2.role: super_admin / admin / manager / staff)
#   2. 部门负责人 (Department.manager_id == employee_id)
#   3. 职位编码 (Position.code 匹配预设映射)
#   4. 项目角色 (ProjectTeamMember.role_code + is_leader)
# ============================================================

# ============================================================
# 隐式权限映射表
# ============================================================
# 基于 Position.name（中文名）映射到权限组
# 规则：只要担任该职位，就自动拥有对应权限，无需手动授权
# 权限层级：店长 > 主管 > 规划师/客户经理 > 设计师/导购 > 专员
# ============================================================

# --- 权限组定义 ---
# 每个权限组定义一组权限，多个职位可以共享同一个权限组

# 门店管理层：店长/副店长 — 门店内全模块管理
_PERM_STORE_EXEC = {
    'permissions': [
        'admin.dashboard.view',
        # 线索与客户
        'lead.view', 'lead.create', 'lead.update', 'lead.follow', 'lead.assign', 'lead.stats.view',
        'customer.view', 'customer.create', 'customer.update',
        'building.view', 'building.create', 'building.update', 'building.follow',
        # 报价与合同
        'quote.view', 'quote.create', 'quote.update', 'quote.approve',
        'contract.view', 'contract.create', 'contract.update', 'contract.flow', 'contract.payment',
        # 案例与选品
        'case.view', 'case.create', 'case.update', 'case.publish',
        'scheme.view',
        # 项目与任务
        'project.view', 'project.create',
        'task.publish', 'task.review',
        'meeting.manage', 'review.manage',
        # 财务与成本
        'finance.view', 'cost.view', 'cost.calculate',
        # 知识库
        'knowledge.view', 'knowledge.create', 'knowledge.update',
        # 服务流程与预约
        'workflow.view', 'appointment.view',
        # 员工查看
        'employee.view',
    ],
    'scope': 'store',
}

# 运营主管 — 门店运营管理（略低于店长，无财务/合同付款权限）
_PERM_OPS_MANAGER = {
    'permissions': [
        'admin.dashboard.view',
        'lead.view', 'lead.create', 'lead.update', 'lead.follow', 'lead.assign', 'lead.stats.view',
        'customer.view', 'customer.create', 'customer.update',
        'building.view', 'building.create', 'building.update', 'building.follow',
        'quote.view', 'quote.create', 'quote.update',
        'contract.view', 'contract.create', 'contract.update', 'contract.flow',
        'case.view', 'case.create', 'case.update',
        'scheme.view',
        'project.view', 'project.create',
        'task.publish', 'task.review',
        'meeting.manage', 'review.manage',
        'cost.view', 'cost.calculate',
        'knowledge.view', 'knowledge.create',
        'workflow.view', 'appointment.view',
        'employee.view',
    ],
    'scope': 'store',
}

# 销售主管 — 线索/客户/合同/预约管理
_PERM_SALES_MANAGER = {
    'permissions': [
        'admin.dashboard.view',
        'lead.view', 'lead.create', 'lead.update', 'lead.follow', 'lead.assign', 'lead.stats.view',
        'customer.view', 'customer.create', 'customer.update',
        'building.view', 'building.create', 'building.update', 'building.follow',
        'contract.view', 'contract.create', 'contract.update', 'contract.flow',
        'quote.view', 'quote.create', 'quote.update',
        'appointment.view',
        'project.view',
        'case.view',
        'finance.view',
    ],
    'scope': 'store',
}

# 设计主管 — 设计部全模块（案例/报价/选品/知识库/任务审核）
_PERM_DESIGN_DIRECTOR = {
    'permissions': [
        'admin.dashboard.view',
        'case.view', 'case.create', 'case.update', 'case.publish',
        'quote.view', 'quote.create', 'quote.update', 'quote.approve',
        'scheme.view',
        'knowledge.view', 'knowledge.create', 'knowledge.update',
        'project.view', 'project.create',
        'task.publish', 'task.review',
        'meeting.manage', 'review.manage', 'review.write',
        'customer.view',
        'employee.view',
    ],
    'scope': 'store',
}

# 工程主管 — 施工流程/合同/成本/项目
_PERM_ENGINEERING_MANAGER = {
    'permissions': [
        'admin.dashboard.view',
        'workflow.view',
        'contract.view', 'contract.update',
        'project.view', 'project.create', 'project.update',
        'task.publish', 'task.review', 'task.accept', 'task.report',
        'meeting.manage', 'review.manage', 'review.write',
        'cost.view', 'cost.calculate',
        'finance.view',
        'knowledge.view',
        'case.view',
        'employee.view',
    ],
    'scope': 'store',
}

# 全案客户经理/家居顾问 — 报价+客户+案例+项目参与
_PERM_ACCOUNT_MANAGER = {
    'permissions': [
        'admin.dashboard.view',
        'quote.view', 'quote.create', 'quote.update',
        'customer.view', 'customer.create', 'customer.update',
        'case.view',
        'building.view',
        'project.view', 'task.accept', 'task.report', 'task.apply',
        'meeting.apply', 'review.write',
        'knowledge.view',
        'scheme.view', 'workflow.view',
        'lead.view', 'lead.create', 'lead.update', 'lead.follow',
        'appointment.view',
    ],
    'scope': 'store',
}

# 家居规划师 — 报价+客户+案例+项目参与
_PERM_PLANNER = {
    'permissions': [
        'admin.dashboard.view',
        'quote.view', 'quote.create', 'quote.update',
        'customer.view', 'customer.create', 'customer.update',
        'case.view',
        'building.view',
        'project.view', 'task.accept', 'task.report', 'task.apply',
        'meeting.apply', 'review.write',
        'knowledge.view',
        'scheme.view', 'workflow.view',
    ],
    'scope': 'store',
}

# 资深/首席全案设计师 — 案例+报价+选品+知识库+项目参与
_PERM_SENIOR_DESIGNER = {
    'permissions': [
        'admin.dashboard.view',
        'case.view', 'case.create', 'case.update',
        'quote.view', 'quote.create', 'quote.update',
        'scheme.view',
        'knowledge.view', 'knowledge.create',
        'project.view', 'task.accept', 'task.report', 'task.apply',
        'meeting.apply', 'review.write',
        'customer.view',
        'workflow.view',
    ],
    'scope': 'store',
}

# 普通全案设计师 — 案例+选品+知识库+项目参与
_PERM_DESIGNER = {
    'permissions': [
        'admin.dashboard.view',
        'case.view', 'case.create', 'case.update',
        'scheme.view',
        'knowledge.view', 'knowledge.create',
        'project.view', 'task.accept', 'task.report', 'task.apply',
        'meeting.apply', 'review.write',
        'quote.view',
        'workflow.view',
    ],
    'scope': 'store',
}

# 实习设计师 — 案例+选品+知识库（无报价创建权限）
_PERM_INTERN_DESIGNER = {
    'permissions': [
        'admin.dashboard.view',
        'case.view',
        'scheme.view',
        'knowledge.view',
        'project.view', 'task.accept', 'task.report',
        'meeting.apply',
        'quote.view',
    ],
    'scope': 'store',
}

# 效果图设计师/酷家乐绘图员 — 案例+选品+知识库
_PERM_VISUAL_DESIGNER = {
    'permissions': [
        'admin.dashboard.view',
        'case.view', 'case.create', 'case.update',
        'scheme.view',
        'knowledge.view',
        'project.view', 'task.accept', 'task.report',
        'meeting.apply',
    ],
    'scope': 'store',
}

# 软装搭配设计师 — 选品+案例+知识库
_PERM_SOFT_DESIGNER = {
    'permissions': [
        'admin.dashboard.view',
        'scheme.view',
        'case.view', 'case.create', 'case.update',
        'knowledge.view', 'knowledge.create',
        'project.view', 'task.accept', 'task.report',
        'meeting.apply', 'review.write',
    ],
    'scope': 'store',
}

# 门店导购 — 线索+客户+预约+案例查看
_PERM_GUIDE = {
    'permissions': [
        'admin.dashboard.view',
        'lead.view', 'lead.create', 'lead.update', 'lead.follow',
        'customer.view', 'customer.create', 'customer.update',
        'building.view',
        'appointment.view',
        'case.view',
        'quote.view',
        'scheme.view',
        'project.view',
    ],
    'scope': 'store',
}

# 渠道业务员/楼盘地推专员 — 线索+客户+楼盘+预约
_PERM_FIELD_SALES = {
    'permissions': [
        'admin.dashboard.view',
        'lead.view', 'lead.create', 'lead.update', 'lead.follow',
        'customer.view', 'customer.create', 'customer.update',
        'building.view', 'building.create', 'building.update', 'building.follow',
        'appointment.view',
        'project.view',
    ],
    'scope': 'store',
}

# 家装谈单专员 — 报价+客户+合同
_PERM_NEGOTIATOR = {
    'permissions': [
        'admin.dashboard.view',
        'quote.view', 'quote.create', 'quote.update',
        'customer.view', 'customer.create', 'customer.update',
        'contract.view', 'contract.create', 'contract.update',
        'case.view',
        'project.view',
    ],
    'scope': 'store',
}

# 预算报价专员 — 报价全权限+成本
_PERM_QUOTE_SPECIALIST = {
    'permissions': [
        'admin.dashboard.view',
        'quote.view', 'quote.create', 'quote.update', 'quote.approve',
        'cost.view', 'cost.calculate',
        'customer.view',
        'contract.view',
        'case.view',
        'project.view',
    ],
    'scope': 'store',
}

# 物料跟单员 — 报价查看+物料+案例
_PERM_MATERIAL_TRACKER = {
    'permissions': [
        'admin.dashboard.view',
        'quote.view',
        'case.view',
        'scheme.view',
        'knowledge.view',
        'project.view', 'task.accept', 'task.report',
    ],
    'scope': 'store',
}

# 工程监理/巡检专员 — 施工流程+合同+项目+任务
_PERM_SUPERVISOR = {
    'permissions': [
        'admin.dashboard.view',
        'workflow.view',
        'contract.view', 'contract.update',
        'project.view',
        'task.accept', 'task.report', 'task.review',
        'meeting.apply', 'review.write',
        'cost.view',
        'case.view',
        'knowledge.view',
    ],
    'scope': 'store',
}

# 安装师傅/硬装施工工长/施工师傅/水电木瓦油工 — 项目参与+任务接收
_PERM_WORKER = {
    'permissions': [
        'admin.dashboard.view',
        'project.view', 'task.accept', 'task.report',
        'meeting.apply',
        'workflow.view',
    ],
    'scope': 'store',
}

# 售后维保专员 — 项目+任务+客户
_PERM_AFTER_SALES = {
    'permissions': [
        'admin.dashboard.view',
        'project.view', 'task.accept', 'task.report',
        'customer.view',
        'workflow.view',
        'meeting.apply',
    ],
    'scope': 'store',
}

# 暖通施工专员 — 项目+任务+流程
_PERM_HVAC = {
    'permissions': [
        'admin.dashboard.view',
        'project.view', 'task.accept', 'task.report',
        'workflow.view',
        'meeting.apply',
    ],
    'scope': 'store',
}

# 前台接待 — 客户+预约+线索查看
_PERM_RECEPTIONIST = {
    'permissions': [
        'admin.dashboard.view',
        'customer.view', 'customer.create',
        'appointment.view',
        'lead.view',
    ],
    'scope': 'store',
}

# 门店文员 — 员工查看+客户查看+预约
_PERM_CLERK = {
    'permissions': [
        'admin.dashboard.view',
        'employee.view',
        'customer.view',
        'appointment.view',
        'project.view',
    ],
    'scope': 'store',
}

# 短视频运营/新媒体专员 — 案例+知识库
_PERM_MEDIA = {
    'permissions': [
        'admin.dashboard.view',
        'case.view', 'case.create', 'case.update',
        'knowledge.view', 'knowledge.create',
        'scheme.view',
    ],
    'scope': 'store',
}

# 培训讲师/培训专员/商学院培训导师 — 知识库全权限
_PERM_TRAINER = {
    'permissions': [
        'admin.dashboard.view',
        'knowledge.view', 'knowledge.create', 'knowledge.update', 'knowledge.share',
        'case.view',
    ],
    'scope': 'store',
}

# 产品研发专员/系统研发专员/总部研发团队 — 知识库+案例+选品
_PERM_RND = {
    'permissions': [
        'admin.dashboard.view',
        'knowledge.view', 'knowledge.create', 'knowledge.update', 'knowledge.delete',
        'case.view', 'case.create', 'case.update',
        'scheme.view',
        'employee.view',
    ],
    'scope': 'global',
}

# 库管仓储员 — 项目+物料+任务
_PERM_WAREHOUSE = {
    'permissions': [
        'admin.dashboard.view',
        'project.view', 'task.accept', 'task.report',
        'case.view',
        'knowledge.view',
    ],
    'scope': 'store',
}

# 全案样板设计团队 — 案例+选品+知识库+项目
_PERM_DESIGN_TEAM = {
    'permissions': [
        'admin.dashboard.view',
        'case.view', 'case.create', 'case.update',
        'scheme.view',
        'knowledge.view', 'knowledge.create',
        'project.view', 'task.accept', 'task.report',
        'meeting.apply', 'review.write',
    ],
    'scope': 'store',
}

# 楼盘地推团队 — 线索+客户+楼盘
_PERM_FIELD_TEAM = {
    'permissions': [
        'admin.dashboard.view',
        'lead.view', 'lead.create', 'lead.update', 'lead.follow',
        'customer.view', 'customer.create', 'customer.update',
        'building.view', 'building.create', 'building.update', 'building.follow',
        'appointment.view',
    ],
    'scope': 'store',
}

# 培训团队 — 知识库+案例
_PERM_TRAINING_TEAM = {
    'permissions': [
        'admin.dashboard.view',
        'knowledge.view', 'knowledge.create', 'knowledge.update',
        'case.view',
    ],
    'scope': 'store',
}

# --- 职位名称 → 权限组映射 ---
# 键为 Position.name（中文职位名），值为上面定义的权限组变量
POSITION_IMPLICIT_PERMISSIONS = {
    # 门店管理层
    '店长': _PERM_STORE_EXEC,
    '副店长': _PERM_STORE_EXEC,
    # 主管级
    '运营主管': _PERM_OPS_MANAGER,
    '销售主管': _PERM_SALES_MANAGER,
    '设计主管': _PERM_DESIGN_DIRECTOR,
    '工程主管': _PERM_ENGINEERING_MANAGER,
    # 客户经理/顾问/规划师
    '全案客户经理': _PERM_ACCOUNT_MANAGER,
    '家居顾问': _PERM_ACCOUNT_MANAGER,
    '家居规划师': _PERM_PLANNER,
    # 设计师
    '首席全案设计师': _PERM_SENIOR_DESIGNER,
    '资深全案设计师': _PERM_SENIOR_DESIGNER,
    '普通全案设计师': _PERM_DESIGNER,
    '实习设计师': _PERM_INTERN_DESIGNER,
    '效果图设计师': _PERM_VISUAL_DESIGNER,
    '酷家乐绘图员': _PERM_VISUAL_DESIGNER,
    '软装搭配设计师': _PERM_SOFT_DESIGNER,
    '全案样板设计团队': _PERM_DESIGN_TEAM,
    # 销售/导购
    '门店导购': _PERM_GUIDE,
    '渠道业务员': _PERM_FIELD_SALES,
    '楼盘地推专员': _PERM_FIELD_SALES,
    '楼盘地推团队': _PERM_FIELD_TEAM,
    '家装谈单专员': _PERM_NEGOTIATOR,
    # 报价/物料
    '预算报价专员': _PERM_QUOTE_SPECIALIST,
    '物料跟单员': _PERM_MATERIAL_TRACKER,
    # 工程施工
    '工程监理': _PERM_SUPERVISOR,
    '巡检专员': _PERM_SUPERVISOR,
    '安装师傅': _PERM_WORKER,
    '硬装施工工长': _PERM_WORKER,
    '硬装施工师傅': _PERM_WORKER,
    '水电工': _PERM_WORKER,
    '木工': _PERM_WORKER,
    '瓦工': _PERM_WORKER,
    '油工': _PERM_WORKER,
    '暖通施工专员': _PERM_HVAC,
    '售后维保专员': _PERM_AFTER_SALES,
    # 行政/前台
    '前台接待': _PERM_RECEPTIONIST,
    '门店文员': _PERM_CLERK,
    # 新媒体
    '短视频运营': _PERM_MEDIA,
    '新媒体专员': _PERM_MEDIA,
    # 培训
    '培训讲师': _PERM_TRAINER,
    '培训专员': _PERM_TRAINER,
    '商学院培训导师': _PERM_TRAINER,
    '培训团队': _PERM_TRAINING_TEAM,
    # 研发
    '总部研发团队': _PERM_RND,
    '产品研发专员': _PERM_RND,
    '系统研发专员': _PERM_RND,
    # 仓储
    '库管仓储员': _PERM_WAREHOUSE,
}

# --- 部门负责人隐式权限 ---
# 部门负责人（manager_id 指向的员工）自动拥有本部门管理权限
# 此外，主管级职位（运营/销售/设计/工程主管）自动视为对应部门的负责人
DEPT_MANAGER_PERMISSIONS = {
    'employee.view',
    'project.view',
    'project.create',
    'knowledge.view', 'knowledge.create',
}

# 主管职位 → 对应部门编码映射（用于部门负责人隐式权限）
POSITION_TO_DEPARTMENT = {
    '店长': '管理',
    '副店长': '管理',
    '运营主管': '管理',
    '销售主管': '市场',
    '设计主管': '设计',
    '工程主管': '工程',
}

# --- 项目角色隐式权限（完整版） ---
# 项目组长自动获得的权限（scope=project）
PROJECT_LEADER_ALL_PERMISSIONS = {
    'project.view', 'project.update', 'project.archive',
    'project.member.manage', 'project.permission.assign',
    'task.publish', 'task.review',
    'meeting.apply', 'meeting.manage',
    'review.write', 'review.manage',
    'cost.view', 'cost.calculate',
}

# 项目成员默认权限（scope=project）
PROJECT_MEMBER_ALL_PERMISSIONS = {
    'project.view', 'task.accept', 'task.report', 'task.apply',
    'meeting.apply', 'review.write',
}


PERMISSION_REGISTRY = [
    {'key': 'admin.dashboard.view', 'label': '查看管理后台首页', 'group': '管理后台', 'scope': 'global'},
    {'key': 'employee.view', 'label': '查看员工档案', 'group': '员工管理', 'scope': 'store'},
    {'key': 'employee.create', 'label': '新建员工', 'group': '员工管理', 'scope': 'store'},
    {'key': 'employee.update', 'label': '编辑员工档案', 'group': '员工管理', 'scope': 'store'},
    {'key': 'employee.delete', 'label': '停用/删除员工', 'group': '员工管理', 'scope': 'store'},
    {'key': 'employee.permission.assign', 'label': '分配员工权限', 'group': '员工管理', 'scope': 'store'},
    {'key': 'org.department.manage', 'label': '管理部门', 'group': '组织架构', 'scope': 'store'},
    {'key': 'org.position.manage', 'label': '管理岗位', 'group': '组织架构', 'scope': 'store'},
    {'key': 'project.view', 'label': '查看项目组', 'group': '项目组织', 'scope': 'project'},
    {'key': 'project.create', 'label': '新建项目组', 'group': '项目组织', 'scope': 'store'},
    {'key': 'project.update', 'label': '编辑项目组', 'group': '项目组织', 'scope': 'project'},
    {'key': 'project.archive', 'label': '归档项目组', 'group': '项目组织', 'scope': 'project'},
    {'key': 'project.member.manage', 'label': '管理项目成员', 'group': '项目组织', 'scope': 'project'},
    {'key': 'project.permission.assign', 'label': '分配项目权限', 'group': '项目组织', 'scope': 'project'},
    {'key': 'task.publish', 'label': '发布任务', 'group': '任务流程', 'scope': 'project'},
    {'key': 'task.accept', 'label': '接收任务', 'group': '任务流程', 'scope': 'project'},
    {'key': 'task.report', 'label': '提交任务汇报', 'group': '任务流程', 'scope': 'project'},
    {'key': 'task.review', 'label': '审核任务', 'group': '任务流程', 'scope': 'project'},
    {'key': 'task.apply', 'label': '主动申请任务', 'group': '任务流程', 'scope': 'project'},
    {'key': 'meeting.apply', 'label': '发起会议', 'group': '会议复盘', 'scope': 'project'},
    {'key': 'meeting.manage', 'label': '管理会议', 'group': '会议复盘', 'scope': 'project'},
    {'key': 'review.write', 'label': '编写项目复盘', 'group': '会议复盘', 'scope': 'project'},
    {'key': 'review.manage', 'label': '归档项目复盘', 'group': '会议复盘', 'scope': 'project'},
    {'key': 'cost.view', 'label': '查看项目预算', 'group': '成本分配', 'scope': 'project'},
    {'key': 'cost.calculate', 'label': '成本汇算', 'group': '成本分配', 'scope': 'project'},
    {'key': 'commission.manage', 'label': '项目提成', 'group': '成本分配', 'scope': 'project'},
    {'key': 'profit.distribute', 'label': '利润分配', 'group': '成本分配', 'scope': 'project'},
    {'key': 'lead.view', 'label': '查看线索', 'group': '线索管理', 'scope': 'store'},
    {'key': 'lead.create', 'label': '新建线索', 'group': '线索管理', 'scope': 'store'},
    {'key': 'lead.update', 'label': '编辑线索', 'group': '线索管理', 'scope': 'store'},
    {'key': 'lead.delete', 'label': '删除线索', 'group': '线索管理', 'scope': 'store'},
    {'key': 'lead.follow', 'label': '跟进线索', 'group': '线索管理', 'scope': 'store'},
    {'key': 'lead.assign', 'label': '分配线索', 'group': '线索管理', 'scope': 'store'},
    {'key': 'lead.stats.view', 'label': '查看线索统计', 'group': '线索管理', 'scope': 'store'},
    {'key': 'customer.view', 'label': '查看客户', 'group': '客户管理', 'scope': 'store'},
    {'key': 'customer.create', 'label': '新建客户', 'group': '客户管理', 'scope': 'store'},
    {'key': 'customer.update', 'label': '编辑客户', 'group': '客户管理', 'scope': 'store'},
    {'key': 'customer.delete', 'label': '删除客户', 'group': '客户管理', 'scope': 'store'},
    {'key': 'building.view', 'label': '查看楼盘', 'group': '楼盘管理', 'scope': 'store'},
    {'key': 'building.create', 'label': '新建楼盘', 'group': '楼盘管理', 'scope': 'store'},
    {'key': 'building.update', 'label': '编辑楼盘', 'group': '楼盘管理', 'scope': 'store'},
    {'key': 'building.delete', 'label': '删除楼盘', 'group': '楼盘管理', 'scope': 'store'},
    {'key': 'building.follow', 'label': '楼盘跟进', 'group': '楼盘管理', 'scope': 'store'},
    {'key': 'contract.view', 'label': '查看合同', 'group': '合同管理', 'scope': 'store'},
    {'key': 'contract.create', 'label': '新建合同', 'group': '合同管理', 'scope': 'store'},
    {'key': 'contract.update', 'label': '编辑合同', 'group': '合同管理', 'scope': 'store'},
    {'key': 'contract.delete', 'label': '删除合同', 'group': '合同管理', 'scope': 'store'},
    {'key': 'contract.flow', 'label': '合同流转', 'group': '合同管理', 'scope': 'store'},
    {'key': 'contract.payment', 'label': '登记合同收款', 'group': '合同管理', 'scope': 'store'},
    {'key': 'contract.template.manage', 'label': '管理合同模板', 'group': '合同管理', 'scope': 'store'},
    {'key': 'quote.view', 'label': '查看报价', 'group': '报价管理', 'scope': 'store'},
    {'key': 'quote.create', 'label': '新建报价', 'group': '报价管理', 'scope': 'store'},
    {'key': 'quote.update', 'label': '编辑报价', 'group': '报价管理', 'scope': 'store'},
    {'key': 'quote.delete', 'label': '删除报价', 'group': '报价管理', 'scope': 'store'},
    {'key': 'quote.approve', 'label': '审核报价', 'group': '报价管理', 'scope': 'store'},
    {'key': 'quote.template.manage', 'label': '管理报价模板/规则', 'group': '报价管理', 'scope': 'store'},
    {'key': 'case.view', 'label': '查看案例', 'group': '案例管理', 'scope': 'store'},
    {'key': 'case.create', 'label': '新建案例', 'group': '案例管理', 'scope': 'store'},
    {'key': 'case.update', 'label': '编辑案例', 'group': '案例管理', 'scope': 'store'},
    {'key': 'case.delete', 'label': '删除案例', 'group': '案例管理', 'scope': 'store'},
    {'key': 'case.publish', 'label': '发布案例', 'group': '案例管理', 'scope': 'store'},
    {'key': 'case.template.manage', 'label': '管理案例模板', 'group': '案例管理', 'scope': 'store'},
    {'key': 'knowledge.view', 'label': '查看知识库', 'group': '知识库管理', 'scope': 'store'},
    {'key': 'knowledge.create', 'label': '新建知识内容', 'group': '知识库管理', 'scope': 'store'},
    {'key': 'knowledge.update', 'label': '编辑知识内容', 'group': '知识库管理', 'scope': 'store'},
    {'key': 'knowledge.delete', 'label': '删除知识内容', 'group': '知识库管理', 'scope': 'store'},
    {'key': 'knowledge.share', 'label': '分享知识内容', 'group': '知识库管理', 'scope': 'store'},
    {'key': 'scheme.view', 'label': '查看选品', 'group': '选品管理', 'scope': 'store'},
    {'key': 'workflow.view', 'label': '查看服务流程', 'group': '服务流程', 'scope': 'store'},
    {'key': 'appointment.view', 'label': '查看预约', 'group': '预约管理', 'scope': 'store'},
    {'key': 'finance.view', 'label': '查看财务', 'group': '财务管理', 'scope': 'store'},
]

PROJECT_LEADER_GRANTABLE = {
    'project.view', 'task.accept', 'task.report', 'task.apply',
    'meeting.apply', 'review.write'
}

PROJECT_MEMBER_DEFAULTS = {
    'project.view', 'task.accept', 'task.report', 'task.apply', 'meeting.apply'
}

STORE_MANAGER_GRANTABLE_GROUPS = {
    '管理后台', '员工管理', '组织架构', '项目组织', '任务流程', '会议复盘',
    '线索管理', '客户管理', '楼盘管理', '合同管理', '报价管理', '案例管理',
    '知识库管理', '选品管理', '服务流程', '预约管理', '财务管理'
}

MODULE_PERMISSIONS = [
    {'key': 'dashboard', 'label': '管理首页', 'path': '/admin/dashboard', 'permission_key': 'admin.dashboard.view'},
    {'key': 'buildings', 'label': '楼盘管理', 'path': '/admin/buildings', 'permission_key': 'building.view'},
    {'key': 'leads', 'label': '线索管理', 'path': '/admin/leads', 'permission_key': 'lead.view'},
    {'key': 'customers', 'label': '客户管理', 'path': '/admin/customers', 'permission_key': 'customer.view'},
    {'key': 'cases', 'label': '案例管理', 'path': '/admin/cases', 'permission_key': 'case.view'},
    {'key': 'schemes', 'label': '选品管理', 'path': '/admin/schemes', 'permission_key': 'scheme.view'},
    {'key': 'quotes', 'label': '报价管理', 'path': '/admin/quotes', 'permission_key': 'quote.view'},
    {'key': 'contracts', 'label': '合同管理', 'path': '/admin/contracts', 'permission_key': 'contract.view'},
    {'key': 'workflow', 'label': '服务流程', 'path': '/admin/workflow', 'permission_key': 'workflow.view'},
    {'key': 'appointments', 'label': '预约管理', 'path': '/admin/appointments', 'permission_key': 'appointment.view'},
    {'key': 'finance', 'label': '财务管理', 'path': '/admin/finance', 'permission_key': 'finance.view'},
    {'key': 'settings', 'label': '系统设置', 'path': '/admin/settings', 'permission_key': 'employee.view'},
    {'key': 'knowledge', 'label': '知识库管理', 'path': '/admin/knowledge', 'permission_key': 'knowledge.view'},
]


def permission_groups():
    groups = {}
    for item in PERMISSION_REGISTRY:
        groups.setdefault(item['group'], []).append(item)
    return [{'group': group, 'items': items} for group, items in groups.items()]


def permission_item(permission_key):
    return next((item for item in PERMISSION_REGISTRY if item['key'] == permission_key), None)


def visible_modules(current_user):
    """返回当前用户可见的模块列表，走完整的 has_permission 逻辑（含隐式权限）"""
    return [
        item for item in MODULE_PERMISSIONS
        if has_permission(current_user, item['permission_key'], 'store', current_user.get('store_id'))
    ]


def is_super_admin(current_user):
    return current_user.get('role') in ['super_admin']


def is_admin(current_user):
    return current_user.get('role') in ['super_admin', 'admin']


def current_employee_id(current_user):
    if current_user.get('employee_id'):
        return current_user.get('employee_id')
    user = UserV2.query.get(current_user.get('id')) if current_user.get('id') else None
    return user.employee_id if user else None


def _assignment_query(current_user, permission_key):
    user_id = current_user.get('id')
    employee_id = current_employee_id(current_user)
    query = PermissionAssignment.query.filter_by(permission_key=permission_key, is_active=True)
    if user_id and employee_id:
        query = query.filter(db.or_(
            PermissionAssignment.user_id == user_id,
            PermissionAssignment.employee_id == employee_id
        ))
    elif user_id:
        query = query.filter(PermissionAssignment.user_id == user_id)
    elif employee_id:
        query = query.filter(PermissionAssignment.employee_id == employee_id)
    return query


def _scope_matches(assignment, scope_type=None, scope_id=None):
    if not assignment.is_effective():
        return False
    if assignment.scope_type == 'global':
        return True
    if not scope_type:
        return True
    if assignment.scope_type == scope_type and (
        assignment.scope_id is None or scope_id is None or int(assignment.scope_id) == int(scope_id)
    ):
        return True
    return False


def is_project_leader(current_user, project_id):
    employee_id = current_employee_id(current_user)
    if not employee_id or not project_id:
        return False
    project = ProjectTeam.query.filter_by(id=project_id, is_deleted=False).first()
    if project and project.owner_id == employee_id:
        return True
    return ProjectTeamMember.query.filter_by(
        project_id=project_id,
        employee_id=employee_id,
        is_leader=True
    ).first() is not None


def _get_employee_position_name(employee):
    """获取员工的职位名称，用于隐式权限推导"""
    if not employee or not employee.position_id:
        return None
    position = Position.query.get(employee.position_id)
    if not position:
        return None
    return position.name


def _is_department_manager(current_user, employee_id):
    """判断员工是否是某个部门的负责人（显式 manager_id 或主管职位隐式认定）"""
    if not employee_id:
        return False
    # 1. 显式部门负责人
    dept = Department.query.filter_by(manager_id=employee_id, is_active=True).first()
    if dept:
        return True
    # 2. 隐式：主管职位自动视为对应部门负责人
    employee = Employee.query.get(employee_id)
    if employee and employee.position_id:
        position = Position.query.get(employee.position_id)
        if position and position.name in POSITION_TO_DEPARTMENT:
            return True
    return False


def _check_implicit_permissions(current_user, permission_key, scope_type, scope_id):
    """
    隐式权限推导核心：
    基于员工的职位名称、部门负责人身份、项目角色，自动判定是否有权限。
    无需管理员手动授权。
    
    推导链：
      1. 职位 → 职位权限组（如店长→门店全权限）
      2. 部门负责人/主管职位 → 部门管理权限
      3. 项目组长 → 项目内全权限
      4. 项目成员 → 项目内基础权限
      5. 项目协同/成本核算角色 → 角色对应权限
    """
    employee_id = current_employee_id(current_user)
    if not employee_id:
        return False

    employee = Employee.query.get(employee_id)
    if not employee:
        return False

    # --- 1. 基于职位名称的隐式权限 ---
    position_name = _get_employee_position_name(employee)
    if position_name and position_name in POSITION_IMPLICIT_PERMISSIONS:
        perm_config = POSITION_IMPLICIT_PERMISSIONS[position_name]
        if permission_key in perm_config['permissions']:
            scope_val = perm_config.get('scope', 'store')
            if scope_val == 'global':
                return True
            if scope_val == 'store':
                if scope_type in ['store', None]:
                    return True
                # 跨 scope 也放行（如 project 级别的查看权限）
                if scope_type == 'project':
                    return True
                if scope_type == 'global':
                    return True

    # --- 2. 部门负责人/主管职位隐式权限 ---
    if _is_department_manager(current_user, employee_id):
        if permission_key in DEPT_MANAGER_PERMISSIONS:
            if scope_type in ['store', 'department', None]:
                return True

    # --- 3. 项目组长隐式权限（完整版） ---
    if scope_type == 'project' and scope_id and is_project_leader(current_user, scope_id):
        if permission_key in PROJECT_LEADER_ALL_PERMISSIONS:
            return True

    # --- 4. 项目成员隐式权限 ---
    if scope_type == 'project' and scope_id:
        if permission_key in PROJECT_MEMBER_ALL_PERMISSIONS:
            member = ProjectTeamMember.query.filter_by(
                project_id=scope_id, employee_id=employee_id
            ).first()
            if member:
                return True
        # --- 5. 项目角色模板隐式权限（协同/成本核算等） ---
        member = ProjectTeamMember.query.filter_by(
            project_id=scope_id, employee_id=employee_id
        ).first()
        if member and member.role_code:
            # 根据项目角色模板推导权限
            from app.routes.project_team_routes import PROJECT_ROLE_TEMPLATES
            for template in PROJECT_ROLE_TEMPLATES:
                if template['code'] == member.role_code:
                    if permission_key in template.get('permission_keys', []):
                        return True
                    break

    return False


def has_permission(current_user, permission_key, scope_type=None, scope_id=None):
    # 超级管理员：全权限
    if is_super_admin(current_user):
        return True

    # 系统管理员：全权限
    if is_admin(current_user):
        return True

    # 经理角色：store 级别的模块权限
    if current_user.get('role') == 'manager' and scope_type == 'store' and (
        scope_id is None or current_user.get('store_id') in [None, scope_id]
    ):
        item = permission_item(permission_key)
        if item and item['group'] in STORE_MANAGER_GRANTABLE_GROUPS:
            return True

    # --- 隐式权限推导（职位/部门/项目角色） ---
    if _check_implicit_permissions(current_user, permission_key, scope_type, scope_id):
        return True

    # --- 显式授权（管理员手动分配的权限） ---
    assignments = _assignment_query(current_user, permission_key).all()
    return any(_scope_matches(item, scope_type, scope_id) for item in assignments)


def can_grant_permission(current_user, permission_key, scope_type=None, scope_id=None, target_employee_id=None):
    if is_super_admin(current_user):
        return True

    item = permission_item(permission_key)
    if not item:
        return False

    if current_user.get('role') == 'manager':
        if item['group'] not in STORE_MANAGER_GRANTABLE_GROUPS:
            return False
        if scope_type not in ['store', 'department', 'project', 'self', None]:
            return False
        if target_employee_id:
            employee = Employee.query.get(target_employee_id)
            if employee and current_user.get('store_id') and employee.store_id != current_user.get('store_id'):
                return False
        return True

    if scope_type == 'project' and is_project_leader(current_user, scope_id):
        if permission_key not in PROJECT_LEADER_GRANTABLE:
            return False
        if target_employee_id:
            member = ProjectTeamMember.query.filter_by(project_id=scope_id, employee_id=target_employee_id).first()
            return member is not None
        return True

    return False


def require_permission(permission_key, scope_resolver=None):
    """路由权限装饰器，和 jwt_required_v2 配合使用"""
    def decorator(f):
        @wraps(f)
        def wrapper(current_user, *args, **kwargs):
            scope_type, scope_id = (None, None)
            if scope_resolver:
                scope_type, scope_id = scope_resolver(current_user, *args, **kwargs)
            if not has_permission(current_user, permission_key, scope_type, scope_id):
                return jsonify({'code': 403, 'message': '没有权限执行该操作', 'data': {
                    'permission_key': permission_key,
                    'scope_type': scope_type,
                    'scope_id': scope_id,
                }}), 403
            return f(current_user, *args, **kwargs)
        return wrapper
    return decorator


def create_permission_audit(current_user, action, assignment=None, detail=None, target_user_id=None, target_employee_id=None):
    log = PermissionAuditLog(
        operator_user_id=current_user.get('id'),
        target_user_id=target_user_id or (assignment.user_id if assignment else None),
        target_employee_id=target_employee_id or (assignment.employee_id if assignment else None),
        action=action,
        permission_key=assignment.permission_key if assignment else None,
        scope_type=assignment.scope_type if assignment else None,
        scope_id=assignment.scope_id if assignment else None,
        detail=detail,
    )
    db.session.add(log)
    return log
