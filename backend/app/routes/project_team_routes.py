# -*- coding: utf-8 -*-
"""
项目组织协同 API
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from app import db
from app.models.auth_v2 import UserV2
from app.models.hr import Employee
from app.models.project_team import (
    ProjectMeeting,
    ProjectPermissionPolicy,
    ProjectReview,
    ProjectTask,
    ProjectTaskApplication,
    ProjectTeam,
    ProjectTeamMember,
)
from app.routes.auth_routes_v2 import jwt_required_v2
from app.services.permission_service import current_employee_id, has_permission, require_permission


project_team_bp = Blueprint('project_team', __name__, url_prefix='/api/v3/project-teams')


PROJECT_TYPE_OPTIONS = [
    {'label': '客户项目', 'value': 'customer_project'},
    {'label': '楼盘运营', 'value': 'building_operation'},
    {'label': '新媒体运营', 'value': 'media_operation'},
    {'label': '门店赋能培训', 'value': 'store_training'},
    {'label': '内部专项', 'value': 'internal_project'},
]

PROJECT_STATUS_OPTIONS = [
    {'label': '筹备中', 'value': 'planning'},
    {'label': '进行中', 'value': 'active'},
    {'label': '暂停', 'value': 'paused'},
    {'label': '已完成', 'value': 'completed'},
    {'label': '已归档', 'value': 'archived'},
]

TASK_STATUS_FLOW = {
    'draft': ['published'],
    'published': ['accepted', 'archived'],
    'accepted': ['in_progress'],
    'in_progress': ['submitted'],
    'submitted': ['approved', 'rework'],
    'rework': ['in_progress', 'submitted'],
    'approved': ['archived'],
    'archived': [],
}

PROJECT_ROLE_TEMPLATES = [
    {
        'code': 'leader',
        'name': '项目组长',
        'description': '负责目标拆解、任务发布、审核和复盘。',
        'permission_keys': [
            'project.view', 'project.edit', 'member.manage', 'task.publish',
            'task.review', 'meeting.manage', 'cost.calculate', 'review.manage'
        ],
    },
    {
        'code': 'coordinator',
        'name': '项目协同',
        'description': '负责进度跟进、会议组织和资料归档。',
        'permission_keys': [
            'project.view', 'task.publish', 'task.accept', 'task.report',
            'meeting.manage', 'review.write'
        ],
    },
    {
        'code': 'member',
        'name': '项目成员',
        'description': '按分工接收任务、提交汇报和主动发起任务申请。',
        'permission_keys': ['project.view', 'task.accept', 'task.report', 'task.apply', 'meeting.apply'],
    },
    {
        'code': 'finance',
        'name': '成本核算',
        'description': '查看预算、登记成本、核算提成和利润分配。',
        'permission_keys': ['project.view', 'cost.view', 'cost.calculate', 'commission.manage', 'profit.distribute'],
    },
]

PERMISSION_GROUPS = [
    {
        'group': '项目基础',
        'items': [
            {'key': 'project.view', 'label': '查看项目'},
            {'key': 'project.edit', 'label': '编辑项目'},
            {'key': 'member.manage', 'label': '成员与分工'},
        ],
    },
    {
        'group': '任务流程',
        'items': [
            {'key': 'task.publish', 'label': '发布任务'},
            {'key': 'task.accept', 'label': '接收任务'},
            {'key': 'task.report', 'label': '提交汇报'},
            {'key': 'task.review', 'label': '任务审核'},
            {'key': 'task.apply', 'label': '主动申请任务'},
        ],
    },
    {
        'group': '会议复盘',
        'items': [
            {'key': 'meeting.apply', 'label': '发起会议'},
            {'key': 'meeting.manage', 'label': '会议管理'},
            {'key': 'review.write', 'label': '编写复盘'},
            {'key': 'review.manage', 'label': '归档复盘'},
        ],
    },
    {
        'group': '成本分配',
        'items': [
            {'key': 'cost.view', 'label': '查看预算'},
            {'key': 'cost.calculate', 'label': '成本汇算'},
            {'key': 'commission.manage', 'label': '项目提成'},
            {'key': 'profit.distribute', 'label': '利润分配'},
        ],
    },
]


def _ok(data=None, message='success'):
    return jsonify({'code': 200, 'data': data, 'message': message})


def _bad(message, status=400):
    return jsonify({'code': status, 'data': None, 'message': message}), status


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.fromisoformat(str(value)[:10]).date()
    except ValueError:
        return None


def _parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    raw = str(value).replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        try:
            return datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None


def _as_list(value):
    return value if isinstance(value, list) else []


def _current_employee_id(current_user):
    return current_employee_id(current_user)


def _project_scope(current_user, project_id, *args, **kwargs):
    return 'project', project_id


def _store_scope(current_user, *args, **kwargs):
    return 'store', current_user.get('store_id')


def _visible_project_query(current_user):
    query = ProjectTeam.query.filter_by(is_deleted=False)
    if current_user.get('role') in ['super_admin', 'admin']:
        return query
    employee_id = _current_employee_id(current_user)
    if current_user.get('role') == 'manager':
        return query
    if employee_id:
        return query.join(ProjectTeamMember).filter(ProjectTeamMember.employee_id == employee_id)
    return query.filter(ProjectTeam.id == -1)


def _project_or_404(project_id):
    return ProjectTeam.query.filter_by(id=project_id, is_deleted=False).first_or_404()


def _apply_project_fields(project, data, current_user=None):
    for field in [
        'name', 'code', 'project_type', 'status', 'priority', 'objective', 'scope',
        'owner_id', 'related_lead_id', 'related_building_id', 'related_customer_id',
        'related_contract_id', 'related_quote_id', 'related_case_id', 'review_summary'
    ]:
        if field in data:
            setattr(project, field, data.get(field))
    if 'budget' in data:
        project.budget = data.get('budget') or 0
    if 'spent_amount' in data:
        project.spent_amount = data.get('spent_amount') or 0
    if 'progress' in data:
        project.progress = max(0, min(100, int(data.get('progress') or 0)))
    if 'start_date' in data:
        project.start_date = _parse_date(data.get('start_date'))
    if 'end_date' in data:
        project.end_date = _parse_date(data.get('end_date'))
    if current_user and not project.tenant_id:
        project.tenant_id = current_user.get('tenant_id')


@project_team_bp.route('', methods=['GET'])
@jwt_required_v2
def list_project_teams(current_user):
    page = request.args.get('page', 1, type=int)
    page_size = min(request.args.get('pageSize', 20, type=int), 100)
    keyword = request.args.get('keyword', '').strip()
    status = request.args.get('status')
    project_type = request.args.get('project_type')

    query = _visible_project_query(current_user)
    if keyword:
        query = query.filter(or_(
            ProjectTeam.name.contains(keyword),
            ProjectTeam.code.contains(keyword),
            ProjectTeam.objective.contains(keyword),
        ))
    if status:
        query = query.filter(ProjectTeam.status == status)
    if project_type:
        query = query.filter(ProjectTeam.project_type == project_type)

    total = query.count()
    items = query.order_by(ProjectTeam.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    all_active = _visible_project_query(current_user)
    stats = {
        'total': all_active.count(),
        'active': all_active.filter(ProjectTeam.status == 'active').count(),
        'planning': all_active.filter(ProjectTeam.status == 'planning').count(),
        'completed': all_active.filter(ProjectTeam.status == 'completed').count(),
        'pending_tasks': ProjectTask.query.join(ProjectTeam).filter(
            ProjectTeam.is_deleted.is_(False),
            ProjectTask.status.in_(['published', 'accepted', 'in_progress', 'submitted', 'rework'])
        ).count(),
    }
    return _ok({'items': [item.to_dict() for item in items], 'total': total, 'stats': stats})


@project_team_bp.route('', methods=['POST'])
@jwt_required_v2
@require_permission('project.create', _store_scope)
def create_project_team(current_user):
    data = request.get_json() or {}
    if not data.get('name'):
        return _bad('项目组名称不能为空')

    project = ProjectTeam(created_by=current_user.get('id'))
    _apply_project_fields(project, data, current_user)
    db.session.add(project)
    db.session.flush()

    for member_data in _as_list(data.get('members')):
        employee_id = member_data.get('employee_id')
        if employee_id:
            db.session.add(ProjectTeamMember(
                project_id=project.id,
                employee_id=employee_id,
                role_code=member_data.get('role_code', 'member'),
                responsibility=member_data.get('responsibility'),
                workload=member_data.get('workload'),
                is_leader=bool(member_data.get('is_leader')),
                data_scope=member_data.get('data_scope', 'project'),
                permission_overrides=_as_list(member_data.get('permission_overrides')),
            ))

    db.session.commit()
    return _ok(project.to_dict(include_children=True), '项目组创建成功')


@project_team_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required_v2
def get_project_team(current_user, project_id):
    if not has_permission(current_user, 'project.view', 'project', project_id):
        return _bad('没有权限查看该项目组', 403)
    return _ok(_project_or_404(project_id).to_dict(include_children=True))


@project_team_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required_v2
@require_permission('project.update', _project_scope)
def update_project_team(current_user, project_id):
    project = _project_or_404(project_id)
    _apply_project_fields(project, request.get_json() or {}, current_user)
    db.session.commit()
    return _ok(project.to_dict(include_children=True), '项目组已更新')


@project_team_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required_v2
@require_permission('project.archive', _project_scope)
def delete_project_team(current_user, project_id):
    project = _project_or_404(project_id)
    project.is_deleted = True
    db.session.commit()
    return _ok(True, '项目组已归档')


@project_team_bp.route('/<int:project_id>/members', methods=['POST'])
@jwt_required_v2
@require_permission('project.member.manage', _project_scope)
def add_project_member(current_user, project_id):
    _project_or_404(project_id)
    data = request.get_json() or {}
    if not data.get('employee_id'):
        return _bad('请选择成员')

    member = ProjectTeamMember(
        project_id=project_id,
        employee_id=data.get('employee_id'),
        role_code=data.get('role_code', 'member'),
        responsibility=data.get('responsibility'),
        workload=data.get('workload'),
        is_leader=bool(data.get('is_leader')),
        data_scope=data.get('data_scope', 'project'),
        permission_overrides=_as_list(data.get('permission_overrides')),
    )
    db.session.add(member)
    db.session.commit()
    return _ok(member.to_dict(), '成员已加入项目组')


@project_team_bp.route('/<int:project_id>/members/<int:member_id>', methods=['PUT'])
@jwt_required_v2
@require_permission('project.member.manage', _project_scope)
def update_project_member(current_user, project_id, member_id):
    _project_or_404(project_id)
    member = ProjectTeamMember.query.filter_by(id=member_id, project_id=project_id).first_or_404()
    data = request.get_json() or {}
    for field in ['employee_id', 'role_code', 'responsibility', 'workload', 'data_scope']:
        if field in data:
            setattr(member, field, data.get(field))
    if 'is_leader' in data:
        member.is_leader = bool(data.get('is_leader'))
    if 'permission_overrides' in data:
        member.permission_overrides = _as_list(data.get('permission_overrides'))
    db.session.commit()
    return _ok(member.to_dict(), '成员分工已更新')


@project_team_bp.route('/<int:project_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required_v2
@require_permission('project.member.manage', _project_scope)
def remove_project_member(current_user, project_id, member_id):
    _project_or_404(project_id)
    member = ProjectTeamMember.query.filter_by(id=member_id, project_id=project_id).first_or_404()
    db.session.delete(member)
    db.session.commit()
    return _ok(True, '成员已移出项目组')


def _apply_task_fields(task, data, current_user=None):
    for field in ['title', 'description', 'phase', 'status', 'priority', 'assignee_id', 'reviewer_id', 'report_content', 'review_comment', 'rework_reason', 'source_type']:
        if field in data:
            setattr(task, field, data.get(field))
    if 'publisher_id' in data:
        task.publisher_id = data.get('publisher_id')
    elif current_user and not task.publisher_id:
        task.publisher_id = _current_employee_id(current_user)
    if 'start_date' in data:
        task.start_date = _parse_date(data.get('start_date'))
    if 'due_date' in data:
        task.due_date = _parse_date(data.get('due_date'))
    if 'evidence_files' in data:
        task.evidence_files = _as_list(data.get('evidence_files'))
    if 'sort_order' in data:
        task.sort_order = data.get('sort_order') or 0


@project_team_bp.route('/<int:project_id>/tasks', methods=['POST'])
@jwt_required_v2
@require_permission('task.publish', _project_scope)
def create_project_task(current_user, project_id):
    _project_or_404(project_id)
    data = request.get_json() or {}
    if not data.get('title'):
        return _bad('任务标题不能为空')
    task = ProjectTask(project_id=project_id)
    _apply_task_fields(task, data, current_user)
    db.session.add(task)
    db.session.commit()
    return _ok(task.to_dict(), '任务已创建')


@project_team_bp.route('/<int:project_id>/tasks/<int:task_id>', methods=['PUT'])
@jwt_required_v2
@require_permission('task.publish', _project_scope)
def update_project_task(current_user, project_id, task_id):
    _project_or_404(project_id)
    task = ProjectTask.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    _apply_task_fields(task, request.get_json() or {}, current_user)
    db.session.commit()
    return _ok(task.to_dict(), '任务已更新')


@project_team_bp.route('/<int:project_id>/tasks/<int:task_id>/transition', methods=['POST'])
@jwt_required_v2
def transition_project_task(current_user, project_id, task_id):
    _project_or_404(project_id)
    task = ProjectTask.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    data = request.get_json() or {}
    next_status = data.get('status')
    if next_status not in TASK_STATUS_FLOW.get(task.status, []):
        return _bad('当前任务状态不支持该流转')
    permission_map = {
        'accepted': 'task.accept',
        'in_progress': 'task.report',
        'submitted': 'task.report',
        'approved': 'task.review',
        'rework': 'task.review',
        'archived': 'task.review',
    }
    permission_key = permission_map.get(next_status, 'task.publish')
    if not has_permission(current_user, permission_key, 'project', project_id):
        return _bad('没有权限流转该任务', 403)

    task.status = next_status
    if 'report_content' in data:
        task.report_content = data.get('report_content')
    if 'review_comment' in data:
        task.review_comment = data.get('review_comment')
    if 'rework_reason' in data:
        task.rework_reason = data.get('rework_reason')
    if 'evidence_files' in data:
        task.evidence_files = _as_list(data.get('evidence_files'))
    if next_status == 'approved':
        task.completed_at = datetime.utcnow()
    db.session.commit()
    return _ok(task.to_dict(), '任务状态已更新')


@project_team_bp.route('/<int:project_id>/applications', methods=['POST'])
@jwt_required_v2
@require_permission('task.apply', _project_scope)
def create_task_application(current_user, project_id):
    _project_or_404(project_id)
    data = request.get_json() or {}
    employee_id = data.get('employee_id') or _current_employee_id(current_user)
    if not employee_id:
        return _bad('请选择申请人')
    application = ProjectTaskApplication(
        project_id=project_id,
        employee_id=employee_id,
        task_type=data.get('task_type', 'field_measurement'),
        reason=data.get('reason'),
        related_customer_id=data.get('related_customer_id'),
        related_building_id=data.get('related_building_id'),
        evidence_files=_as_list(data.get('evidence_files')),
    )
    db.session.add(application)
    db.session.commit()
    return _ok(application.to_dict(), '任务申请已提交')


@project_team_bp.route('/<int:project_id>/applications/<int:application_id>/review', methods=['PUT'])
@jwt_required_v2
@require_permission('task.review', _project_scope)
def review_task_application(current_user, project_id, application_id):
    _project_or_404(project_id)
    application = ProjectTaskApplication.query.filter_by(id=application_id, project_id=project_id).first_or_404()
    data = request.get_json() or {}
    status = data.get('status')
    if status not in ['approved', 'rejected']:
        return _bad('审核状态不正确')
    application.status = status
    application.reviewer_id = data.get('reviewer_id') or _current_employee_id(current_user)
    application.review_comment = data.get('review_comment')
    application.reviewed_at = datetime.utcnow()

    task = None
    if status == 'approved' and data.get('create_task', True):
        task = ProjectTask(
            project_id=project_id,
            title=data.get('task_title') or application.task_type or '主动申请任务',
            description=application.reason,
            phase=data.get('phase'),
            status='published',
            priority=data.get('priority', 'normal'),
            publisher_id=application.reviewer_id,
            assignee_id=application.employee_id,
            source_type='application',
            evidence_files=application.evidence_files or [],
        )
        db.session.add(task)
    db.session.commit()
    return _ok({
        'application': application.to_dict(),
        'task': task.to_dict() if task else None,
    }, '任务申请审核完成')


@project_team_bp.route('/<int:project_id>/meetings', methods=['POST'])
@jwt_required_v2
@require_permission('meeting.apply', _project_scope)
def create_project_meeting(current_user, project_id):
    _project_or_404(project_id)
    data = request.get_json() or {}
    if not data.get('topic'):
        return _bad('会议主题不能为空')
    meeting = ProjectMeeting(
        project_id=project_id,
        topic=data.get('topic'),
        problems=data.get('problems'),
        attendee_ids=_as_list(data.get('attendee_ids')),
        required_files=data.get('required_files'),
        required_tools=data.get('required_tools'),
        location=data.get('location'),
        duration_minutes=data.get('duration_minutes') or 60,
        start_time=_parse_datetime(data.get('start_time')),
        secretary_id=data.get('secretary_id'),
        minutes=data.get('minutes'),
        decisions=data.get('decisions'),
        status=data.get('status', 'planned'),
        created_by=current_user.get('id'),
    )
    db.session.add(meeting)
    db.session.commit()
    return _ok(meeting.to_dict(), '会议已登记')


@project_team_bp.route('/<int:project_id>/meetings/<int:meeting_id>', methods=['PUT'])
@jwt_required_v2
@require_permission('meeting.manage', _project_scope)
def update_project_meeting(current_user, project_id, meeting_id):
    _project_or_404(project_id)
    meeting = ProjectMeeting.query.filter_by(id=meeting_id, project_id=project_id).first_or_404()
    data = request.get_json() or {}
    for field in ['topic', 'problems', 'required_files', 'required_tools', 'location', 'duration_minutes', 'secretary_id', 'minutes', 'decisions', 'status']:
        if field in data:
            setattr(meeting, field, data.get(field))
    if 'attendee_ids' in data:
        meeting.attendee_ids = _as_list(data.get('attendee_ids'))
    if 'start_time' in data:
        meeting.start_time = _parse_datetime(data.get('start_time'))
    if data.get('status') == 'archived':
        meeting.archived_at = datetime.utcnow()
    db.session.commit()
    return _ok(meeting.to_dict(), '会议已更新')


@project_team_bp.route('/<int:project_id>/reviews', methods=['POST'])
@jwt_required_v2
@require_permission('review.write', _project_scope)
def create_project_review(current_user, project_id):
    project = _project_or_404(project_id)
    data = request.get_json() or {}
    review = ProjectReview(
        project_id=project_id,
        summary=data.get('summary'),
        wins=data.get('wins'),
        problems=data.get('problems'),
        budget_review=data.get('budget_review'),
        schedule_review=data.get('schedule_review'),
        improvement_actions=data.get('improvement_actions'),
        created_by=current_user.get('id'),
    )
    if data.get('summary'):
        project.review_summary = data.get('summary')
    db.session.add(review)
    db.session.commit()
    return _ok(review.to_dict(), '项目复盘已保存')


@project_team_bp.route('/<int:project_id>/permission-policies', methods=['PUT'])
@jwt_required_v2
@require_permission('project.permission.assign', _project_scope)
def save_permission_policies(current_user, project_id):
    _project_or_404(project_id)
    data = request.get_json() or {}
    policies = _as_list(data.get('policies'))
    ProjectPermissionPolicy.query.filter_by(project_id=project_id).delete()
    for item in policies:
        if item.get('permission_key'):
            db.session.add(ProjectPermissionPolicy(
                project_id=project_id,
                permission_key=item.get('permission_key'),
                allowed_roles=_as_list(item.get('allowed_roles')),
                allowed_employee_ids=_as_list(item.get('allowed_employee_ids')),
                approval_required=bool(item.get('approval_required')),
            ))
    db.session.commit()
    saved = ProjectPermissionPolicy.query.filter_by(project_id=project_id).all()
    return _ok([item.to_dict() for item in saved], '项目权限已更新')


@project_team_bp.route('/roles', methods=['GET'])
@jwt_required_v2
def get_project_roles(current_user):
    return _ok(PROJECT_ROLE_TEMPLATES)


@project_team_bp.route('/permissions', methods=['GET'])
@jwt_required_v2
def get_project_permissions(current_user):
    return _ok({
        'groups': PERMISSION_GROUPS,
        'project_types': PROJECT_TYPE_OPTIONS,
        'project_statuses': PROJECT_STATUS_OPTIONS,
        'task_status_flow': TASK_STATUS_FLOW,
    })


@project_team_bp.route('/employee-options', methods=['GET'])
@jwt_required_v2
def get_employee_options(current_user):
    employees = Employee.query.filter(Employee.is_deleted.is_(False), Employee.status.in_(['active', 'probation'])).order_by(Employee.name).all()
    return _ok([{
        'id': item.id,
        'name': item.name,
        'department_name': item.department.name if item.department else None,
        'position_name': item.position.name if item.position else None,
    } for item in employees])


@project_team_bp.route('/employee/<int:employee_id>/summary', methods=['GET'])
@jwt_required_v2
def get_employee_project_summary(current_user, employee_id):
    """员工在项目组织中的项目、任务和权限概览"""
    memberships = ProjectTeamMember.query.join(ProjectTeam).filter(
        ProjectTeamMember.employee_id == employee_id,
        ProjectTeam.is_deleted.is_(False)
    ).order_by(ProjectTeam.updated_at.desc()).all()
    project_ids = [item.project_id for item in memberships]
    tasks = []
    if project_ids:
        tasks = ProjectTask.query.filter(
            ProjectTask.project_id.in_(project_ids),
            ProjectTask.assignee_id == employee_id,
            ProjectTask.status.in_(['published', 'accepted', 'in_progress', 'submitted', 'rework'])
        ).order_by(ProjectTask.due_date.asc(), ProjectTask.id.desc()).limit(20).all()

    projects = []
    for member in memberships:
        project = member.project
        role = next((item for item in PROJECT_ROLE_TEMPLATES if item['code'] == member.role_code), None)
        projects.append({
            'project': project.to_dict(),
            'member': member.to_dict(),
            'role_permissions': role['permission_keys'] if role else [],
        })

    return _ok({
        'projects': projects,
        'tasks': [item.to_dict() for item in tasks],
        'stats': {
            'project_count': len(projects),
            'active_task_count': len(tasks),
            'leader_project_count': len([item for item in memberships if item.is_leader]),
        }
    })
