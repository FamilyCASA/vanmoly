# -*- coding: utf-8 -*-
"""
细粒度权限管理 API
"""
from datetime import datetime
from flask import Blueprint, jsonify, request

from app import db
from app.models.auth_v2 import UserV2
from app.models.hr import Employee
from app.models.permission import PermissionAssignment, PermissionAuditLog
from app.models.project_team import ProjectTask, ProjectTeam, ProjectTeamMember
from app.routes.auth_routes_v2 import jwt_required_v2
from app.services.permission_service import (
    can_grant_permission,
    create_permission_audit,
    current_employee_id,
    has_permission,
    permission_groups,
    visible_modules,
    PROJECT_LEADER_ALL_PERMISSIONS,
    PROJECT_MEMBER_ALL_PERMISSIONS,
)


permission_bp = Blueprint('permission', __name__, url_prefix='/api/v3/permissions')


def _ok(data=None, message='success'):
    return jsonify({'code': 200, 'data': data, 'message': message})


def _bad(message, status=400):
    return jsonify({'code': status, 'data': None, 'message': message}), status


def _parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None


def _is_super_admin(current_user):
    return current_user.get('role') == 'super_admin'


def _manageable_employee_query(current_user):
    query = Employee.query.filter(Employee.is_deleted.is_(False))
    if _is_super_admin(current_user):
        return query
    if current_user.get('role') == 'manager' and current_user.get('store_id'):
        return query.filter(Employee.store_id == current_user.get('store_id'))
    return query.filter(Employee.id == current_employee_id(current_user))


@permission_bp.route('/registry', methods=['GET'])
@jwt_required_v2
def get_permission_registry(current_user):
    """权限注册表，前端用于构建权限中心"""
    return _ok({
        'groups': permission_groups(),
        'scope_types': [
            {'label': '全系统', 'value': 'global'},
            {'label': '门店', 'value': 'store'},
            {'label': '部门', 'value': 'department'},
            {'label': '项目组', 'value': 'project'},
            {'label': '本人', 'value': 'self'},
        ],
        'grant_rules': {
            'super_admin': '可分配所有管理层和业务权限',
            'manager': '可分配本门店员工的门店/项目相关权限',
            'project_leader': '可分配本项目成员的项目内执行权限',
        }
    })


@permission_bp.route('/my-implicit-permissions', methods=['GET'])
@jwt_required_v2
def get_my_implicit_permissions(current_user):
    """
    查询当前用户的隐式权限来源（职位/部门负责人/项目角色）。
    用于前端展示"无需手动授权，自动获得"的权限来源说明。
    """
    from app.services.permission_service import (
        POSITION_IMPLICIT_PERMISSIONS,
        POSITION_TO_DEPARTMENT,
        _get_employee_position_name,
        _is_department_manager,
        is_project_leader,
    )
    from app.models.hr import Department, Position

    employee_id = current_employee_id(current_user)
    sources = []

    if employee_id:
        employee = Employee.query.get(employee_id)

        # 1. 职位来源
        position_name = _get_employee_position_name(employee)
        if position_name and position_name in POSITION_IMPLICIT_PERMISSIONS:
            config = POSITION_IMPLICIT_PERMISSIONS[position_name]
            sources.append({
                'type': 'position',
                'label': f'职位：{position_name}',
                'permissions': config.get('permissions', []),
                'scope': config.get('scope', 'store'),
            })

        # 2. 部门负责人来源
        if _is_department_manager(current_user, employee_id):
            # 查找具体部门
            dept = Department.query.filter_by(manager_id=employee_id, is_active=True).first()
            if dept:
                sources.append({
                    'type': 'department_manager',
                    'label': f'部门负责人：{dept.name}',
                    'permissions': list({'employee.view', 'project.view', 'project.create', 'knowledge.view', 'knowledge.create'}),
                    'scope': 'department',
                })
            elif position_name and position_name in POSITION_TO_DEPARTMENT:
                dept_code = POSITION_TO_DEPARTMENT[position_name]
                dept = Department.query.filter_by(code=dept_code).first()
                dept_display = dept.name if dept else f"{dept_code}部"
                sources.append({
                    'type': 'department_manager',
                    'label': f'部门负责人（{position_name}）：{dept_display}',
                    'permissions': list({'employee.view', 'project.view', 'project.create', 'knowledge.view', 'knowledge.create'}),
                    'scope': 'department',
                })

        # 3. 项目角色来源（列出当前参与的所有项目）
        memberships = ProjectTeamMember.query.filter_by(
            employee_id=employee_id
        ).join(ProjectTeam).filter(
            ProjectTeam.is_deleted.is_(False)
        ).all()
        for member in memberships:
            project = ProjectTeam.query.get(member.project_id)
            if project:
                role_code = member.role_code or ('leader' if member.is_leader else 'member')
                # 获取角色对应的权限
                from app.routes.project_team_routes import PROJECT_ROLE_TEMPLATES
                role_perms = []
                if member.is_leader:
                    role_perms = list(PROJECT_LEADER_ALL_PERMISSIONS)
                else:
                    for template in PROJECT_ROLE_TEMPLATES:
                        if template['code'] == role_code:
                            role_perms = template.get('permission_keys', [])
                            break
                    if not role_perms:
                        role_perms = list(PROJECT_MEMBER_ALL_PERMISSIONS)
                
                role_label = '项目组长' if member.is_leader else role_code
                sources.append({
                    'type': 'project_role',
                    'label': f'{role_label}：{project.name}',
                    'permissions': role_perms,
                    'scope': 'project',
                    'scope_id': project.id,
                })

    return _ok({
        'sources': sources,
        'system_role': current_user.get('role'),
    })


@permission_bp.route('/manageable-employees', methods=['GET'])
@jwt_required_v2
def get_manageable_employees(current_user):
    employees = _manageable_employee_query(current_user).order_by(Employee.name).all()
    return _ok([{
        'id': item.id,
        'name': item.name,
        'store_id': item.store_id,
        'department_id': item.department_id,
        'department_name': item.department.name if item.department else None,
        'position_name': item.position.name if item.position else None,
    } for item in employees])


@permission_bp.route('/assignments', methods=['GET'])
@jwt_required_v2
def list_permission_assignments(current_user):
    employee_id = request.args.get('employee_id', type=int)
    user_id = request.args.get('user_id', type=int)
    scope_type = request.args.get('scope_type')
    scope_id = request.args.get('scope_id', type=int)

    query = PermissionAssignment.query
    if employee_id:
        target = Employee.query.get_or_404(employee_id)
        if not can_grant_permission(current_user, 'employee.permission.assign', 'store', target.store_id, employee_id):
            return _bad('没有权限查看该员工权限', 403)
        query = query.filter_by(employee_id=employee_id)
    elif user_id:
        target_user = UserV2.query.get_or_404(user_id)
        target_employee_id = target_user.employee_id
        if target_employee_id and not can_grant_permission(current_user, 'employee.permission.assign', 'store', target_user.store_id, target_employee_id):
            return _bad('没有权限查看该账号权限', 403)
        query = query.filter_by(user_id=user_id)
    elif not _is_super_admin(current_user):
        own_employee_id = current_employee_id(current_user)
        query = query.filter(db.or_(
            PermissionAssignment.user_id == current_user.get('id'),
            PermissionAssignment.employee_id == own_employee_id
        ))

    if scope_type:
        query = query.filter_by(scope_type=scope_type)
    if scope_id:
        query = query.filter_by(scope_id=scope_id)

    assignments = query.order_by(PermissionAssignment.created_at.desc()).all()
    return _ok([item.to_dict() for item in assignments])


@permission_bp.route('/assignments', methods=['POST'])
@jwt_required_v2
def grant_permission(current_user):
    data = request.get_json() or {}
    # 支持批量分配：permission_keys（数组）或单个 permission_key
    permission_keys = data.get('permission_keys')
    if not permission_keys:
        single = data.get('permission_key')
        permission_keys = [single] if single else []
    target_employee_id = data.get('employee_id')
    target_user_id = data.get('user_id')
    scope_type = data.get('scope_type') or 'global'
    scope_id = data.get('scope_id')

    if not permission_keys:
        return _bad('请选择权限')
    if not target_employee_id and not target_user_id:
        return _bad('请选择授权对象')

    if target_user_id and not target_employee_id:
        user = UserV2.query.get_or_404(target_user_id)
        target_employee_id = user.employee_id

    created = []
    skipped = []
    for pk in permission_keys:
        if not can_grant_permission(current_user, pk, scope_type, scope_id, target_employee_id):
            skipped.append(pk)
            continue
        existing = PermissionAssignment.query.filter_by(
            user_id=target_user_id,
            employee_id=target_employee_id,
            permission_key=pk,
            scope_type=scope_type,
            scope_id=scope_id,
        ).first()
        if existing:
            existing.is_active = True
            existing.expires_at = _parse_datetime(data.get('expires_at'))
            existing.reason = data.get('reason')
            assignment = existing
        else:
            assignment = PermissionAssignment(
                user_id=target_user_id,
                employee_id=target_employee_id,
                permission_key=pk,
                scope_type=scope_type,
                scope_id=scope_id,
                granted_by=current_user.get('id'),
                reason=data.get('reason'),
                expires_at=_parse_datetime(data.get('expires_at')),
            )
            db.session.add(assignment)
        create_permission_audit(current_user, 'grant', assignment, detail=data.get('reason'))
        created.append(assignment)
    db.session.commit()
    result = [a.to_dict() for a in created]
    msg = f'已分配 {len(result)} 项权限'
    if skipped:
        msg += f'，{len(skipped)} 项因权限不足跳过'
    return _ok(result, msg)


@permission_bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
@jwt_required_v2
def revoke_permission(current_user, assignment_id):
    assignment = PermissionAssignment.query.get_or_404(assignment_id)
    if not can_grant_permission(
        current_user,
        assignment.permission_key,
        assignment.scope_type,
        assignment.scope_id,
        assignment.employee_id
    ):
        return _bad('没有权限撤销该权限', 403)
    assignment.is_active = False
    create_permission_audit(current_user, 'revoke', assignment)
    db.session.commit()
    return _ok(True, '权限已撤销')


@permission_bp.route('/me', methods=['GET'])
@jwt_required_v2
def get_my_permissions(current_user):
    """当前账号权限、可见项目和任务卡片"""
    employee_id = current_employee_id(current_user)
    projects = []
    tasks = []
    if employee_id:
        memberships = ProjectTeamMember.query.join(ProjectTeam).filter(
            ProjectTeamMember.employee_id == employee_id,
            ProjectTeam.is_deleted.is_(False)
        ).all()
        project_ids = [item.project_id for item in memberships]
        projects = [item.project.to_dict() for item in memberships if has_permission(current_user, 'project.view', 'project', item.project_id)]
        if project_ids:
            tasks = ProjectTask.query.filter(
                ProjectTask.project_id.in_(project_ids),
                db.or_(ProjectTask.assignee_id == employee_id, ProjectTask.publisher_id == employee_id, ProjectTask.reviewer_id == employee_id),
                ProjectTask.status.in_(['published', 'accepted', 'in_progress', 'submitted', 'rework'])
            ).order_by(ProjectTask.due_date.asc(), ProjectTask.updated_at.desc()).all()

    assignments = PermissionAssignment.query.filter(
        PermissionAssignment.is_active.is_(True),
        db.or_(
            PermissionAssignment.user_id == current_user.get('id'),
            PermissionAssignment.employee_id == employee_id
        )
    ).all()
    return _ok({
        'user': current_user,
        'permissions': [item.to_dict() for item in assignments if item.is_effective()],
        'visible_modules': visible_modules(current_user),
        'projects': projects,
        'task_cards': [item.to_dict() for item in tasks],
    })


@permission_bp.route('/audit-logs', methods=['GET'])
@jwt_required_v2
def get_permission_audit_logs(current_user):
    if not has_permission(current_user, 'employee.permission.assign', 'store', current_user.get('store_id')):
        return _bad('没有权限查看权限日志', 403)
    logs = PermissionAuditLog.query.order_by(PermissionAuditLog.created_at.desc()).limit(200).all()
    return _ok([item.to_dict() for item in logs])
