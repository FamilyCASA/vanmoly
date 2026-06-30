# -*- coding: utf-8 -*-
"""
项目组织协同模型
"""
from datetime import datetime
from app import db
from app.models.hr import Employee


def _date_value(value):
    return value.isoformat() if value else None


def _datetime_value(value):
    return value.strftime('%Y-%m-%d %H:%M:%S') if value else None


class ProjectTeam(db.Model):
    """以项目小组为单位组织客户、楼盘和运营任务"""
    __tablename__ = 'project_team'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    name = db.Column(db.String(100), nullable=False, comment='项目组名称')
    code = db.Column(db.String(40), unique=True, comment='项目编号')
    project_type = db.Column(db.String(30), default='customer_project', comment='项目类型')
    status = db.Column(db.String(30), default='planning', comment='状态')
    priority = db.Column(db.String(20), default='normal', comment='优先级')
    objective = db.Column(db.Text, comment='项目目标')
    scope = db.Column(db.Text, comment='项目范围')
    budget = db.Column(db.Numeric(12, 2), default=0, comment='预算')
    spent_amount = db.Column(db.Numeric(12, 2), default=0, comment='已发生费用')
    progress = db.Column(db.Integer, default=0, comment='项目进度')
    start_date = db.Column(db.Date, comment='开始日期')
    end_date = db.Column(db.Date, comment='计划结束日期')
    owner_id = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='项目负责人')

    related_lead_id = db.Column(db.Integer, comment='关联线索')
    related_building_id = db.Column(db.Integer, comment='关联楼盘')
    related_customer_id = db.Column(db.Integer, comment='关联客户')
    related_contract_id = db.Column(db.Integer, comment='关联合同')
    related_quote_id = db.Column(db.Integer, comment='关联报价')
    related_case_id = db.Column(db.Integer, comment='关联案例')

    review_summary = db.Column(db.Text, comment='项目复盘摘要')
    created_by = db.Column(db.Integer, comment='创建人用户ID')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship('Employee', foreign_keys=[owner_id])
    members = db.relationship('ProjectTeamMember', backref='project', cascade='all, delete-orphan', lazy='dynamic')
    tasks = db.relationship('ProjectTask', backref='project', cascade='all, delete-orphan', lazy='dynamic')
    applications = db.relationship('ProjectTaskApplication', backref='project', cascade='all, delete-orphan', lazy='dynamic')
    meetings = db.relationship('ProjectMeeting', backref='project', cascade='all, delete-orphan', lazy='dynamic')
    reviews = db.relationship('ProjectReview', backref='project', cascade='all, delete-orphan', lazy='dynamic')
    permission_policies = db.relationship('ProjectPermissionPolicy', backref='project', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'code': self.code,
            'project_type': self.project_type,
            'status': self.status,
            'priority': self.priority,
            'objective': self.objective,
            'scope': self.scope,
            'budget': float(self.budget or 0),
            'spent_amount': float(self.spent_amount or 0),
            'progress': self.progress or 0,
            'start_date': _date_value(self.start_date),
            'end_date': _date_value(self.end_date),
            'owner_id': self.owner_id,
            'owner_name': self.owner.name if self.owner else None,
            'related_lead_id': self.related_lead_id,
            'related_building_id': self.related_building_id,
            'related_customer_id': self.related_customer_id,
            'related_contract_id': self.related_contract_id,
            'related_quote_id': self.related_quote_id,
            'related_case_id': self.related_case_id,
            'review_summary': self.review_summary,
            'member_count': self.members.count(),
            'task_count': self.tasks.count(),
            'pending_task_count': self.tasks.filter(ProjectTask.status.in_(['published', 'accepted', 'in_progress', 'submitted', 'rework'])).count(),
            'created_at': _datetime_value(self.created_at),
            'updated_at': _datetime_value(self.updated_at),
        }
        if include_children:
            data.update({
                'members': [item.to_dict() for item in self.members.order_by(ProjectTeamMember.is_leader.desc(), ProjectTeamMember.id).all()],
                'tasks': [item.to_dict() for item in self.tasks.order_by(ProjectTask.sort_order, ProjectTask.id).all()],
                'applications': [item.to_dict() for item in self.applications.order_by(ProjectTaskApplication.created_at.desc()).all()],
                'meetings': [item.to_dict() for item in self.meetings.order_by(ProjectMeeting.start_time.desc()).all()],
                'reviews': [item.to_dict() for item in self.reviews.order_by(ProjectReview.created_at.desc()).all()],
                'permission_policies': [item.to_dict() for item in self.permission_policies.order_by(ProjectPermissionPolicy.permission_key).all()],
            })
        return data


class ProjectTeamMember(db.Model):
    """项目小组成员及其项目内权限"""
    __tablename__ = 'project_team_member'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project_team.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    role_code = db.Column(db.String(40), default='member', comment='项目角色')
    responsibility = db.Column(db.Text, comment='分工职责')
    workload = db.Column(db.String(50), comment='投入比例/工作量')
    is_leader = db.Column(db.Boolean, default=False, comment='是否组长')
    data_scope = db.Column(db.String(30), default='project', comment='数据范围')
    permission_overrides = db.Column(db.JSON, default=list, comment='额外权限')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'department_name': self.employee.department.name if self.employee and self.employee.department else None,
            'position_name': self.employee.position.name if self.employee and self.employee.position else None,
            'role_code': self.role_code,
            'responsibility': self.responsibility,
            'workload': self.workload,
            'is_leader': self.is_leader,
            'data_scope': self.data_scope,
            'permission_overrides': self.permission_overrides or [],
            'joined_at': _datetime_value(self.joined_at),
        }


class ProjectTask(db.Model):
    """项目任务，和服务流程节点保持弱关联"""
    __tablename__ = 'project_task'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project_team.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False, comment='任务标题')
    description = db.Column(db.Text, comment='任务说明')
    phase = db.Column(db.String(50), comment='服务流程阶段/节点')
    status = db.Column(db.String(30), default='draft', comment='任务状态')
    priority = db.Column(db.String(20), default='normal', comment='优先级')
    publisher_id = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='发布人')
    assignee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='执行人')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='审核人')
    start_date = db.Column(db.Date, comment='开始日期')
    due_date = db.Column(db.Date, comment='截止日期')
    completed_at = db.Column(db.DateTime, comment='完成时间')
    evidence_files = db.Column(db.JSON, default=list, comment='任务凭证')
    report_content = db.Column(db.Text, comment='汇报内容')
    review_comment = db.Column(db.Text, comment='审核意见')
    rework_reason = db.Column(db.Text, comment='重做原因')
    source_type = db.Column(db.String(30), default='assigned', comment='来源')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    publisher = db.relationship('Employee', foreign_keys=[publisher_id])
    assignee = db.relationship('Employee', foreign_keys=[assignee_id])
    reviewer = db.relationship('Employee', foreign_keys=[reviewer_id])

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'phase': self.phase,
            'status': self.status,
            'priority': self.priority,
            'publisher_id': self.publisher_id,
            'publisher_name': self.publisher.name if self.publisher else None,
            'assignee_id': self.assignee_id,
            'assignee_name': self.assignee.name if self.assignee else None,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.name if self.reviewer else None,
            'start_date': _date_value(self.start_date),
            'due_date': _date_value(self.due_date),
            'completed_at': _datetime_value(self.completed_at),
            'evidence_files': self.evidence_files or [],
            'report_content': self.report_content,
            'review_comment': self.review_comment,
            'rework_reason': self.rework_reason,
            'source_type': self.source_type,
            'sort_order': self.sort_order,
            'created_at': _datetime_value(self.created_at),
            'updated_at': _datetime_value(self.updated_at),
        }


class ProjectTaskApplication(db.Model):
    """员工主动发起的任务申请"""
    __tablename__ = 'project_task_application'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project_team.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    task_type = db.Column(db.String(50), default='field_measurement', comment='任务类型')
    reason = db.Column(db.Text, comment='申请原因')
    related_customer_id = db.Column(db.Integer, comment='关联客户')
    related_building_id = db.Column(db.Integer, comment='关联楼盘')
    evidence_files = db.Column(db.JSON, default=list, comment='凭证')
    status = db.Column(db.String(20), default='pending', comment='状态')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='审核人')
    review_comment = db.Column(db.Text, comment='审核意见')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)

    employee = db.relationship('Employee', foreign_keys=[employee_id])
    reviewer = db.relationship('Employee', foreign_keys=[reviewer_id])

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'task_type': self.task_type,
            'reason': self.reason,
            'related_customer_id': self.related_customer_id,
            'related_building_id': self.related_building_id,
            'evidence_files': self.evidence_files or [],
            'status': self.status,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.name if self.reviewer else None,
            'review_comment': self.review_comment,
            'created_at': _datetime_value(self.created_at),
            'reviewed_at': _datetime_value(self.reviewed_at),
        }


class ProjectMeeting(db.Model):
    """项目会议申请、纪要与归档"""
    __tablename__ = 'project_meeting'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project_team.id'), nullable=False)
    topic = db.Column(db.String(150), nullable=False, comment='会议主题')
    problems = db.Column(db.Text, comment='需要解决的问题')
    attendee_ids = db.Column(db.JSON, default=list, comment='参会人员')
    required_files = db.Column(db.Text, comment='准备文件')
    required_tools = db.Column(db.Text, comment='准备工具')
    location = db.Column(db.String(120), comment='会议地点')
    duration_minutes = db.Column(db.Integer, default=60, comment='持续时间')
    start_time = db.Column(db.DateTime, comment='开始时间')
    secretary_id = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='书记员')
    minutes = db.Column(db.Text, comment='会议纪要')
    decisions = db.Column(db.Text, comment='会议决议')
    status = db.Column(db.String(30), default='planned', comment='状态')
    created_by = db.Column(db.Integer, comment='申请人用户ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    archived_at = db.Column(db.DateTime)

    secretary = db.relationship('Employee')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'topic': self.topic,
            'problems': self.problems,
            'attendee_ids': self.attendee_ids or [],
            'required_files': self.required_files,
            'required_tools': self.required_tools,
            'location': self.location,
            'duration_minutes': self.duration_minutes,
            'start_time': _datetime_value(self.start_time),
            'secretary_id': self.secretary_id,
            'secretary_name': self.secretary.name if self.secretary else None,
            'minutes': self.minutes,
            'decisions': self.decisions,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': _datetime_value(self.created_at),
            'archived_at': _datetime_value(self.archived_at),
        }


class ProjectReview(db.Model):
    """项目复盘"""
    __tablename__ = 'project_review'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project_team.id'), nullable=False)
    summary = db.Column(db.Text, comment='复盘总结')
    wins = db.Column(db.Text, comment='有效经验')
    problems = db.Column(db.Text, comment='问题记录')
    budget_review = db.Column(db.Text, comment='预算复盘')
    schedule_review = db.Column(db.Text, comment='进度复盘')
    improvement_actions = db.Column(db.Text, comment='改进动作')
    created_by = db.Column(db.Integer, comment='创建人用户ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'summary': self.summary,
            'wins': self.wins,
            'problems': self.problems,
            'budget_review': self.budget_review,
            'schedule_review': self.schedule_review,
            'improvement_actions': self.improvement_actions,
            'created_by': self.created_by,
            'created_at': _datetime_value(self.created_at),
        }


class ProjectPermissionPolicy(db.Model):
    """项目内角色/人员权限策略"""
    __tablename__ = 'project_permission_policy'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project_team.id'), nullable=False)
    permission_key = db.Column(db.String(80), nullable=False, comment='权限键')
    allowed_roles = db.Column(db.JSON, default=list, comment='允许角色')
    allowed_employee_ids = db.Column(db.JSON, default=list, comment='允许员工')
    approval_required = db.Column(db.Boolean, default=False, comment='是否需要审核')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'permission_key': self.permission_key,
            'allowed_roles': self.allowed_roles or [],
            'allowed_employee_ids': self.allowed_employee_ids or [],
            'approval_required': self.approval_required,
            'created_at': _datetime_value(self.created_at),
            'updated_at': _datetime_value(self.updated_at),
        }
