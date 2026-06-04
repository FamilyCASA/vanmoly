"""
人力资源管理系统 V2.0 API路由
所有模型统一在主数据库
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.hr import Department, Position, Employee
from app.models.hr_v2 import (
    EmployeeSalary, PerformanceReview, EmployeePoints, PointsTransaction,
    CareerPath, TrainingRecord, EmployeeWelfare,
    PointsRule, PointsAudit, TeamBuilding, PointsExchange
)
from app.routes.auth_routes_v2 import jwt_required_v2, hash_password, DEFAULT_PASSWORD
from datetime import datetime
from app.models.auth_v2 import UserV2

hr_v2_bp = Blueprint('hr_v2', __name__, url_prefix='/api/v3/hr')


# ========== 部门管理 ==========

@hr_v2_bp.route('/departments', methods=['GET'])
@jwt_required_v2
def get_departments(current_user):
    """获取部门列表"""
    departments = Department.query.order_by(Department.id).all()
    return jsonify({
        'code': 200,
        'data': [d.to_dict() for d in departments],
        'message': 'success'
    })


@hr_v2_bp.route('/departments', methods=['POST'])
@jwt_required_v2
def create_department(current_user):
    """创建部门"""
    data = request.get_json()
    dept = Department(
        code=data['code'],
        name=data['name'],
        parent_id=data.get('parent_id'),
        manager_id=data.get('manager_id'),
        sort_order=data.get('sort_order', 0)
    )
    db.session.add(dept)
    db.session.commit()
    return jsonify({
        'code': 200,
        'data': dept.to_dict(),
        'message': '部门创建成功'
    })


# ========== 岗位管理 ==========

@hr_v2_bp.route('/positions', methods=['GET'])
@jwt_required_v2
def get_positions(current_user):
    """获取岗位列表"""
    positions = Position.query.all()
    return jsonify({
        'code': 200,
        'data': [p.to_dict() for p in positions],
        'message': 'success'
    })


@hr_v2_bp.route('/positions', methods=['POST'])
@jwt_required_v2
def create_position(current_user):
    """创建岗位"""
    data = request.get_json()
    pos = Position(
        code=data['code'],
        name=data['name'],
        department_id=data.get('department_id'),
        level=data.get('level', 1),
        job_type=data.get('job_type'),
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max')
    )
    db.session.add(pos)
    db.session.commit()
    return jsonify({
        'code': 200,
        'data': pos.to_dict(),
        'message': '岗位创建成功'
    })


# ========== 员工管理 ==========

@hr_v2_bp.route('/employees', methods=['GET'])
@jwt_required_v2
def get_employees(current_user):
    """获取员工列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    keyword = request.args.get('keyword', '')
    department_id = request.args.get('department_id', type=int)
    status = request.args.get('status', 'active')
    talent_level = request.args.get('talent_level')
    
    query = Employee.query
    
    if keyword:
        query = query.filter(
            db.or_(
                Employee.name.contains(keyword),
                Employee.employee_no.contains(keyword),
                Employee.phone.contains(keyword)
            )
        )
    
    if department_id:
        query = query.filter_by(department_id=department_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if talent_level:
        query = query.filter_by(talent_level=talent_level)
    
    total = query.count()
    employees = query.order_by(Employee.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # 加载关联数据
    result = []
    for emp in employees:
        emp_data = emp.to_dict()
        # 加载关联登录账号
        user_account = UserV2.query.filter_by(employee_id=emp.id).first()
        if user_account:
            emp_data['account'] = {
                'user_id': user_account.id,
                'username': user_account.username,
                'role': user_account.role,
                'status': user_account.status,
                'must_change_password': user_account.must_change_password,
                'last_login_at': user_account.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if user_account.last_login_at else None,
                'is_resigned': user_account.status == 'resigned',
            }
        else:
            emp_data['account'] = None
        # 加载积分
        points = EmployeePoints.query.filter_by(employee_id=emp.id).first()
        emp_data['points'] = points.to_dict() if points else None
        # 加载最新绩效
        latest_perf = PerformanceReview.query.filter_by(employee_id=emp.id).order_by(PerformanceReview.created_at.desc()).first()
        emp_data['latest_performance'] = latest_perf.to_dict() if latest_perf else None
        # 加载本月薪酬
        current_month = datetime.now()
        current_salary = EmployeeSalary.query.filter_by(
            employee_id=emp.id,
            year=current_month.year,
            month=current_month.month
        ).first()
        emp_data['current_salary'] = current_salary.to_dict() if current_salary else None
        # 加载成长路径
        career = CareerPath.query.filter_by(employee_id=emp.id, status='active').first()
        emp_data['career_path'] = career.to_dict() if career else None
        result.append(emp_data)
    
    return jsonify({
        'code': 200,
        'data': {
            'items': result,
            'total': total,
            'page': page,
            'pageSize': page_size
        },
        'message': 'success'
    })


@hr_v2_bp.route('/employees', methods=['POST'])
@jwt_required_v2
def create_employee(current_user):
    """创建员工"""
    data = request.get_json()
    
    # 生成工号（如果没有提供）
    employee_no = data.get('employee_no')
    if not employee_no:
        last_emp = Employee.query.order_by(Employee.id.desc()).first()
        next_id = (last_emp.id + 1) if last_emp else 1
        employee_no = f"VM{next_id:04d}"
    
    # Handle entry_date conversion
    entry_date_val = data.get('entry_date')
    if entry_date_val and isinstance(entry_date_val, str):
        try:
            entry_date_val = datetime.strptime(entry_date_val[:10], '%Y-%m-%d').date()
        except ValueError:
            entry_date_val = None

    emp = Employee(
        employee_no=employee_no,
        name=data['name'],
        gender=data.get('gender'),
        phone=data.get('phone'),
        email=data.get('email'),
        department_id=data.get('department_id'),
        position_id=data.get('position_id'),
        job_level=data.get('job_level', '1'),
        entry_date=entry_date_val,
        role=data.get('role', 'employee'),
        status=data.get('status', 'active')
    )
    try:
        db.session.add(emp)
        db.session.flush()
        
        # 创建积分账户
        points_account = EmployeePoints(employee_id=emp.id)
        db.session.add(points_account)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': emp.to_dict(),
            'message': '员工创建成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'data': None, 'message': str(e)}), 500


@hr_v2_bp.route('/employees/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_employee(current_user, id):
    """更新员工"""
    emp = Employee.query.get_or_404(id)
    data = request.get_json()
    
    emp.name = data.get('name', emp.name)
    emp.gender = data.get('gender', emp.gender)
    emp.phone = data.get('phone', emp.phone)
    emp.email = data.get('email', emp.email)
    emp.department_id = data.get('department_id', emp.department_id)
    emp.position_id = data.get('position_id', emp.position_id)
    emp.job_level = data.get('job_level', emp.job_level)
    emp.role = data.get('role', emp.role)
    emp.status = data.get('status', emp.status)
    # entry_date 处理
    entry_date_val = data.get('entry_date')
    if entry_date_val and isinstance(entry_date_val, str):
        try:
            emp.entry_date = datetime.strptime(entry_date_val[:10], '%Y-%m-%d').date()
        except ValueError:
            pass
    # is_key_talent / talent_level 字段已从 Employee 模型移除，跳过
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': emp.to_dict(),
        'message': '员工更新成功'
    })


@hr_v2_bp.route('/employees/<int:id>', methods=['GET'])
@jwt_required_v2
def get_employee_detail(current_user, id):
    """获取员工详情"""
    emp = Employee.query.get_or_404(id)
    
    data = emp.to_dict(include_sensitive=True)
    
    # 加载积分
    points = EmployeePoints.query.filter_by(employee_id=id).first()
    data['points'] = points.to_dict() if points else None
    
    # 加载薪酬历史
    salaries = EmployeeSalary.query.filter_by(employee_id=id).order_by(
        EmployeeSalary.year.desc(), EmployeeSalary.month.desc()
    ).limit(12).all()
    data['salaries'] = [s.to_dict() for s in salaries]
    
    # 加载绩效历史
    performances = PerformanceReview.query.filter_by(employee_id=id).order_by(
        PerformanceReview.review_year.desc(), PerformanceReview.review_quarter.desc()
    ).limit(8).all()
    data['performances'] = [p.to_dict() for p in performances]
    
    return jsonify({
        'code': 200,
        'data': data,
        'message': 'success'
    })


# ========== 薪酬管理 ==========

@hr_v2_bp.route('/employees/<int:employee_id>/salaries', methods=['GET'])
@jwt_required_v2
def get_employee_salaries(current_user, employee_id):
    """获取员工薪酬记录"""
    salaries = EmployeeSalary.query.filter_by(employee_id=employee_id).order_by(
        EmployeeSalary.year.desc(), EmployeeSalary.month.desc()
    ).all()
    return jsonify({
        'code': 200,
        'data': [s.to_dict() for s in salaries],
        'message': 'success'
    })


@hr_v2_bp.route('/employees/<int:employee_id>/salaries', methods=['POST'])
@jwt_required_v2
def create_salary(current_user, employee_id):
    """创建薪酬记录"""
    data = request.get_json()
    
    salary = EmployeeSalary(
        employee_id=employee_id,
        year=data['year'],
        month=data['month'],
        base_salary=data.get('base_salary', 0),
        position_allowance=data.get('position_allowance', 0),
        performance_allowance=data.get('performance_allowance', 0),
        seniority_allowance=data.get('seniority_allowance', 0),
        commission=data.get('commission', 0),
        project_bonus=data.get('project_bonus', 0),
        attendance_bonus=data.get('attendance_bonus', 0),
        other_bonus=data.get('other_bonus', 0),
        social_insurance=data.get('social_insurance', 0),
        housing_fund=data.get('housing_fund', 0),
        personal_tax=data.get('personal_tax', 0),
        other_deduction=data.get('other_deduction', 0)
    )
    
    # 计算应发和实发
    salary.calculate_net()
    
    db.session.add(salary)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': salary.to_dict(),
        'message': '薪酬记录创建成功'
    })


# ========== 积分管理 ==========

@hr_v2_bp.route('/employees/<int:employee_id>/points/transactions', methods=['GET'])
@jwt_required_v2
def get_points_transactions(current_user, employee_id):
    """获取积分流水"""
    transactions = PointsTransaction.query.filter_by(employee_id=employee_id).order_by(
        PointsTransaction.created_at.desc()
    ).all()
    return jsonify({
        'code': 200,
        'data': [t.to_dict() for t in transactions],
        'message': 'success'
    })


@hr_v2_bp.route('/employees/<int:employee_id>/points/award', methods=['POST'])
@jwt_required_v2
def award_points(current_user, employee_id):
    """奖励积分"""
    data = request.get_json()
    points = data.get('points', 0)
    description = data.get('description', '')
    
    # 获取积分账户
    account = EmployeePoints.query.filter_by(employee_id=employee_id).first()
    if not account:
        return jsonify({'code': 404, 'message': '积分账户不存在'}), 404
    
    # 创建交易记录
    transaction = PointsTransaction(
        employee_id=employee_id,
        type='earn',
        points=points,
        balance_after=account.current_points + points,
        source_type='manual',
        description=description,
        created_by=request.current_user.get("id")
    )
    db.session.add(transaction)
    
    # 更新账户
    account.current_points += points
    account.total_earned += points
    account.update_level()
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': account.to_dict(),
        'message': f'成功奖励 {points} 积分'
    })


# ========== 统计看板 ==========

@hr_v2_bp.route('/dashboard', methods=['GET'])
@jwt_required_v2
def get_hr_dashboard(current_user):
    """HR仪表盘数据"""
    today = datetime.now()
    
    # 员工统计
    total_employees = Employee.query.filter(Employee.status.in_(['active', 'probation'])).count()
    new_this_month = Employee.query.filter(
        db.extract('year', Employee.created_at) == today.year,
        db.extract('month', Employee.created_at) == today.month
    ).count()
    
    # 生日统计（本月）
    birthday_count = Employee.query.filter(
        db.extract('month', Employee.birthday) == today.month,
        Employee.status == 'active'
    ).count()
    
    # 入职周年（本月）
    anniversary_count = Employee.query.filter(
        db.extract('month', Employee.entry_date) == today.month,
        Employee.status == 'active'
    ).count()
    
    # 即将转正
    probation_count = Employee.query.filter(
        Employee.status == 'probation',
        Employee.probation_end_date <= today
    ).count()
    
    return jsonify({
        'code': 200,
        'data': {
            'total_employees': total_employees,
            'new_this_month': new_this_month,
            'birthday_count': birthday_count,
            'anniversary_count': anniversary_count,
            'probation_count': probation_count
        },
        'message': 'success'
    })


# ========== 员工账号管理 ==========

@hr_v2_bp.route('/employees/<int:id>/account', methods=['POST'])
@jwt_required_v2
def assign_employee_account(current_user, id):
    """为员工赋予登录账号（关联users_v2）"""
    emp = Employee.query.get_or_404(id)
    data = request.get_json()

    login_name = data.get('login_name', '').strip()
    login_type = data.get('login_type', 'username')  # username or phone
    role = data.get('role', 'staff')  # staff / manager / admin

    if not login_name:
        return jsonify({'code': 400, 'message': '登录名不能为空'}), 400

    # 检查是否已有账号
    existing_user = UserV2.query.filter_by(employee_id=id).first()
    if existing_user:
        return jsonify({'code': 400, 'message': '该员工已有登录账号', 'data': existing_user.to_dict()}), 400

    # 检查登录名是否已被占用
    if login_type == 'phone':
        dup = UserV2.query.filter_by(phone=login_name).first()
    else:
        dup = UserV2.query.filter_by(username=login_name).first()
    if dup:
        return jsonify({'code': 400, 'message': '该登录名已被占用'}), 400

    # 创建 users_v2 账号
    phone = login_name if login_type == 'phone' else (emp.phone or login_name)
    username = login_name if login_type == 'username' else ('emp_' + str(id))

    new_user = UserV2(
        username=username,
        nickname=emp.name or username,
        phone=phone,
        password_hash=hash_password(DEFAULT_PASSWORD),
        must_change_password=True,
        role=role,
        employee_id=id,
        department_id=emp.department_id,
        store_id=emp.store_id,
        status='active'
    )
    db.session.add(new_user)

    # 同步更新 employee 表的 username 字段
    emp.username = username
    emp.role = role

    db.session.commit()

    return jsonify({
        'code': 200,
        'data': {
            'user_id': new_user.id,
            'username': new_user.username,
            'nickname': new_user.nickname,
            'phone': new_user.phone,
            'role': new_user.role,
            'default_password': DEFAULT_PASSWORD,
            'must_change_password': True
        },
        'message': '登录账号创建成功，默认密码: ' + DEFAULT_PASSWORD
    })


@hr_v2_bp.route('/employees/<int:id>/reset-password', methods=['POST'])
@jwt_required_v2
def reset_employee_password(current_user, id):
    """重置员工密码为默认密码"""
    emp = Employee.query.get_or_404(id)

    # 查找关联的 users_v2 账号
    user = UserV2.query.filter_by(employee_id=id).first()
    if not user:
        return jsonify({'code': 404, 'message': '该员工未绑定登录账号'}), 404

    # 重置密码
    user.password_hash = hash_password(DEFAULT_PASSWORD)
    user.must_change_password = True
    user.password_changed_at = None
    user.login_fail_count = 0
    user.locked_until = None
    if user.status == 'locked':
        user.status = 'active'

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '密码已重置为默认密码: ' + DEFAULT_PASSWORD,
        'data': {'default_password': DEFAULT_PASSWORD}
    })


@hr_v2_bp.route('/employees/<int:id>/revoke-account', methods=['POST'])
@jwt_required_v2
def revoke_employee_account(current_user, id):
    """收回员工账号（离职后禁止登录）"""
    emp = Employee.query.get_or_404(id)

    user = UserV2.query.filter_by(employee_id=id).first()
    if not user:
        return jsonify({'code': 404, 'message': '该员工未绑定登录账号'}), 404

    # 设置为 resigned 状态
    user.status = 'resigned'
    user.resigned_at = datetime.now()
    user.resigned_reason = '员工离职，账号收回'
    user.resigned_by = current_user.get('id')

    # 同步更新员工状态
    emp.status = 'leave'
    emp.leave_date = datetime.now()

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '账号已收回，该员工无法再登录系统'
    })


@hr_v2_bp.route('/employees/<int:id>/restore-account', methods=['POST'])
@jwt_required_v2
def restore_employee_account(current_user, id):
    """恢复员工账号（重新激活）"""
    emp = Employee.query.get_or_404(id)

    user = UserV2.query.filter_by(employee_id=id).first()
    if not user:
        return jsonify({'code': 404, 'message': '该员工未绑定登录账号'}), 404

    if user.status != 'resigned':
        return jsonify({'code': 400, 'message': '该账号未处于收回状态，无需恢复'}), 400

    # 恢复账号
    user.status = 'active'
    user.resigned_at = None
    user.resigned_reason = None
    user.resigned_by = None
    user.login_fail_count = 0
    user.locked_until = None
    user.must_change_password = True
    user.password_hash = hash_password(DEFAULT_PASSWORD)

    # 同步恢复员工状态
    emp.status = 'active'
    emp.leave_date = None

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '账号已恢复，默认密码: ' + DEFAULT_PASSWORD
    })
# ========== 我的面板 - 积分/团队 ==========

@hr_v2_bp.route('/me/points', methods=['GET'])
@jwt_required_v2
def get_my_points(current_user):
    """当前用户积分余额"""
    emp_id = current_user.get('employee_id')
    if not emp_id:
        return jsonify({'code': 400, 'message': '未绑定员工账号'}), 400

    account = EmployeePoints.query.filter_by(employee_id=emp_id).first()
    if not account:
        account = EmployeePoints(employee_id=emp_id)
        db.session.add(account)
        db.session.commit()

    return jsonify({
        'code': 200,
        'ok': True,
        'message': 'success',
        'data': account.to_dict()
    })


@hr_v2_bp.route('/me/points/detail', methods=['GET'])
@jwt_required_v2
def get_my_points_detail(current_user):
    """当前用户积分明细列表"""
    emp_id = current_user.get('employee_id')
    if not emp_id:
        return jsonify({'code': 400, 'message': '未绑定员工账号'}), 400

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    query = PointsTransaction.query.filter_by(employee_id=emp_id).order_by(
        PointsTransaction.created_at.desc()
    )
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'ok': True,
        'message': 'success',
        'data': {
            'items': [t.to_dict() for t in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@hr_v2_bp.route('/points/rank', methods=['GET'])
@jwt_required_v2
def get_points_rank(current_user):
    """积分排行榜（当前租户）"""
    tenant_id = current_user.get('tenant_id', '0')
    limit = request.args.get('limit', 20, type=int)

    ranks = db.session.query(
        EmployeePoints, Employee
    ).join(Employee, EmployeePoints.employee_id == Employee.id).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False
    ).order_by(EmployeePoints.current_points.desc()).limit(limit).all()

    result = []
    for i, (points, emp) in enumerate(ranks):
        d = points.to_dict()
        d['rank'] = i + 1
        d['employee_name'] = emp.name
        d['position'] = emp.position
        result.append(d)

    return jsonify({
        'code': 200,
        'ok': True,
        'message': 'success',
        'data': result
    })


@hr_v2_bp.route('/me/team', methods=['GET'])
@jwt_required_v2
def get_my_team(current_user):
    """当前用户的团队信息（部门/门店/成员）"""
    emp_id = current_user.get('employee_id')
    if not emp_id:
        return jsonify({'code': 400, 'message': '未绑定员工账号'}), 400

    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'code': 404, 'message': '员工不存在'}), 404

    dept_name = ''
    if emp.department_id:
        dept = Department.query.get(emp.department_id)
        if dept:
            dept_name = dept.name

    store_name = ''
    if emp.store_id:
        from app.models.auth_v2 import Store
        store = Store.query.get(emp.store_id)
        if store:
            store_name = store.name

    members_query = Employee.query.filter(
        Employee.department_id == emp.department_id,
        Employee.status.in_(['active', 'probation']),
        Employee.is_deleted == False
    )
    members = [{
        'id': e.id,
        'name': e.name,
        'position': e.position,
        'phone': e.phone
    } for e in members_query.all()]

    return jsonify({
        'code': 200,
        'ok': True,
        'message': 'success',
        'data': {
            'department': dept_name,
            'store': store_name,
            'members': members
        }
    })# ========== 积分规则管理 ==========

@hr_v2_bp.route('/points/rules', methods=['GET'])
@jwt_required_v2
def get_points_rules(current_user):
    """获取积分规则列表"""
    tenant_id = current_user.get('tenant_id', 'default')
    category = request.args.get('category')
    is_active = request.args.get('is_active')
    
    query = PointsRule.query.filter_by(tenant_id=tenant_id)
    
    if category:
        query = query.filter_by(category=category)
    if is_active is not None:
        query = query.filter_by(is_active=(is_active == 'true'))
    
    rules = query.order_by(PointsRule.category, PointsRule.id).all()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': 'success',
        'data': [r.to_dict() for r in rules]
    })


@hr_v2_bp.route('/points/rules', methods=['POST'])
@jwt_required_v2
def create_points_rule(current_user):
    """创建积分规则"""
    data = request.get_json()
    
    # 检查 action_key 唯一性
    existing = PointsRule.query.filter_by(action_key=data['action_key']).first()
    if existing:
        return jsonify({'code': 400, 'message': '动作标识已存在'}), 400
    
    rule = PointsRule(
        tenant_id=current_user.get('tenant_id', 'default'),
        action_key=data['action_key'],
        action_name=data['action_name'],
        category=data['category'],
        description=data.get('description'),
        points=data.get('points', 0),
        points_type=data.get('points_type', 'earn'),
        unit=data.get('unit', '次'),
        high_value_enabled=data.get('high_value_enabled', False),
        thresholds=data.get('thresholds', []),
        is_active=data.get('is_active', True),
        is_auditable=data.get('is_auditable', True),
        requires_proof=data.get('requires_proof', False),
        related_table=data.get('related_table'),
        related_action=data.get('related_action'),
        allowed_roles=data.get('allowed_roles', []),
        excluded_roles=data.get('excluded_roles', []),
        created_by=current_user.get('employee_id')
    )
    
    db.session.add(rule)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': '规则创建成功',
        'data': rule.to_dict()
    })


@hr_v2_bp.route('/points/rules/<int:rule_id>', methods=['PUT'])
@jwt_required_v2
def update_points_rule(current_user, rule_id):
    """更新积分规则"""
    rule = PointsRule.query.get(rule_id)
    if not rule:
        return jsonify({'code': 404, 'message': '规则不存在'}), 404
    
    data = request.get_json()
    
    # 检查 action_key 唯一性（如果修改了）
    if 'action_key' in data and data['action_key'] != rule.action_key:
        existing = PointsRule.query.filter_by(action_key=data['action_key']).first()
        if existing:
            return jsonify({'code': 400, 'message': '动作标识已存在'}), 400
        rule.action_key = data['action_key']
    
    # 更新字段
    for field in ['action_name', 'category', 'description', 'points', 'points_type',
                  'unit', 'high_value_enabled', 'thresholds', 'is_active', 'is_auditable',
                  'requires_proof', 'related_table', 'related_action', 'allowed_roles', 'excluded_roles']:
        if field in data:
            setattr(rule, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': '规则更新成功',
        'data': rule.to_dict()
    })


@hr_v2_bp.route('/points/rules/<int:rule_id>', methods=['DELETE'])
@jwt_required_v2
def delete_points_rule(current_user, rule_id):
    """删除积分规则"""
    rule = PointsRule.query.get(rule_id)
    if not rule:
        return jsonify({'code': 404, 'message': '规则不存在'}), 404
    
    db.session.delete(rule)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': '规则删除成功'
    })


# ========== 积分审核 ==========

@hr_v2_bp.route('/points/audit', methods=['GET'])
@jwt_required_v2
def get_points_audits(current_user):
    """获取积分审核列表（管理员查看待审核）"""
    tenant_id = current_user.get('tenant_id', 'default')
    status = request.args.get('status', 'pending')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    query = PointsAudit.query
    
    if status:
        query = query.filter_by(status=status)
    
    # TODO: 根据权限过滤（团队负责人只能看本团队）
    
    total = query.count()
    audits = query.order_by(PointsAudit.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': 'success',
        'data': {
            'items': [a.to_dict() for a in audits],
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })


@hr_v2_bp.route('/points/audit', methods=['POST'])
@jwt_required_v2
def submit_points_audit(current_user):
    """提交积分审核申请"""
    data = request.get_json()
    
    emp_id = current_user.get('employee_id')
    if not emp_id:
        return jsonify({'code': 400, 'message': '未绑定员工账号'}), 400
    
    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'code': 404, 'message': '员工不存在'}), 404
    
    # 查找规则
    rule = PointsRule.query.filter_by(action_key=data['action_key']).first()
    if not rule:
        return jsonify({'code': 404, 'message': '积分规则不存在'}), 404
    
    if not rule.is_active:
        return jsonify({'code': 400, 'message': '该规则已停用'}), 400
    
    # 计算积分（支持高客单叠加）
    points = rule.points
    if rule.high_value_enabled and 'contract_amount' in data:
        amount = data['contract_amount']
        for th in sorted(rule.thresholds or [], key=lambda x: x.get('min', 0)):
            if th.get('min', 0) <= amount < th.get('max', float('inf')):
                points += th.get('bonus', 0)
                break
    
    audit = PointsAudit(
        employee_id=emp_id,
        employee_name=emp.name,
        action_key=rule.action_key,
        action_name=rule.action_name,
        category=rule.category,
        points_applied=points,
        proof_url=data.get('proof_url'),
        remark=data.get('remark'),
        related_table=data.get('related_table'),
        related_id=data.get('related_id'),
        status='pending'
    )
    
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': '积分申请已提交',
        'data': audit.to_dict()
    })


@hr_v2_bp.route('/points/audit/<int:audit_id>/approve', methods=['POST'])
@jwt_required_v2
def approve_points_audit(current_user, audit_id):
    """审核通过积分申请"""
    audit = PointsAudit.query.get(audit_id)
    if not audit:
        return jsonify({'code': 404, 'message': '审核记录不存在'}), 404
    
    if audit.status != 'pending':
        return jsonify({'code': 400, 'message': '该申请已处理'}), 400
    
    emp_id = current_user.get('employee_id')
    emp = Employee.query.get(emp_id) if emp_id else None
    
    # 更新审核状态
    audit.status = 'approved'
    audit.audited_by = emp_id
    audit.audited_by_name = emp.name if emp else None
    audit.audited_at = datetime.utcnow()
    
    # 发放积分
    account = EmployeePoints.query.filter_by(employee_id=audit.employee_id).first()
    if not account:
        account = EmployeePoints(employee_id=audit.employee_id)
        db.session.add(account)
    
    # 增加积分
    account.current_points = float(account.current_points) + audit.points_applied
    account.total_earned = float(account.total_earned) + audit.points_applied
    account.update_level()
    
    # 记录流水
    trans = PointsTransaction(
        employee_id=audit.employee_id,
        type='earn',
        points=audit.points_applied,
        balance_after=account.current_points,
        source_type='audit',
        source_id=audit.id,
        description=f'{audit.action_name}（审核通过）',
        created_by=emp_id
    )
    db.session.add(trans)
    
    audit.points_granted = True
    audit.points_granted_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': '审核通过，积分已发放',
        'data': audit.to_dict()
    })


@hr_v2_bp.route('/points/audit/<int:audit_id>/reject', methods=['POST'])
@jwt_required_v2
def reject_points_audit(current_user, audit_id):
    """审核驳回积分申请"""
    audit = PointsAudit.query.get(audit_id)
    if not audit:
        return jsonify({'code': 404, 'message': '审核记录不存在'}), 404
    
    if audit.status != 'pending':
        return jsonify({'code': 400, 'message': '该申请已处理'}), 400
    
    data = request.get_json()
    reject_reason = data.get('reject_reason', '')
    
    if not reject_reason:
        return jsonify({'code': 400, 'message': '驳回原因必填'}), 400
    
    emp_id = current_user.get('employee_id')
    emp = Employee.query.get(emp_id) if emp_id else None
    
    audit.status = 'rejected'
    audit.audited_by = emp_id
    audit.audited_by_name = emp.name if emp else None
    audit.audited_at = datetime.utcnow()
    audit.reject_reason = reject_reason
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': '审核已驳回',
        'data': audit.to_dict()
    })


# ========== 团队团建 ==========

@hr_v2_bp.route('/team-building', methods=['GET'])
@jwt_required_v2
def get_team_buildings(current_user):
    """获取团建申请列表"""
    tenant_id = current_user.get('tenant_id', 'default')
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    query = TeamBuilding.query.filter_by(tenant_id=tenant_id)
    
    if status:
        query = query.filter_by(status=status)
    
    total = query.count()
    items = query.order_by(TeamBuilding.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': 'success',
        'data': {
            'items': [i.to_dict() for i in items],
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })


@hr_v2_bp.route('/team-building', methods=['POST'])
@jwt_required_v2
def create_team_building(current_user):
    """发起团建申请"""
    data = request.get_json()
    
    emp_id = current_user.get('employee_id')
    if not emp_id:
        return jsonify({'code': 400, 'message': '未绑定员工账号'}), 400
    
    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'code': 404, 'message': '员工不存在'}), 404
    
    member_count = data.get('member_count', 4)
    
    # 计算所需积分和基金
    # 公式：所需积分 = 100000 + (人数-4) × 20000
    # 团建基金 = 10000 + (人数-4) × 1000
    total_points = 100000 + (member_count - 4) * 20000
    fund_amount = 10000 + (member_count - 4) * 1000
    max_reimbursement = fund_amount * 1.5
    
    tb = TeamBuilding(
        tenant_id=current_user.get('tenant_id', 'default'),
        team_name=data.get('team_name', f'{emp.name}团队'),
        leader_id=emp_id,
        leader_name=emp.name,
        member_count=member_count,
        total_points_required=total_points,
        fund_amount=fund_amount,
        max_reimbursement=max_reimbursement,
        member_list=data.get('member_list', []),
        status='voting'
    )
    
    db.session.add(tb)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': '团建申请已创建',
        'data': tb.to_dict()
    })


@hr_v2_bp.route('/team-building/<int:tb_id>/vote', methods=['POST'])
@jwt_required_v2
def vote_team_building(current_user, tb_id):
    """团建投票（参与/不参与）"""
    tb = TeamBuilding.query.get(tb_id)
    if not tb:
        return jsonify({'code': 404, 'message': '团建申请不存在'}), 404
    
    if tb.status != 'voting':
        return jsonify({'code': 400, 'message': '当前状态不允许投票'}), 400
    
    data = request.get_json()
    emp_id = current_user.get('employee_id')
    agree = data.get('agree', True)
    
    if agree:
        if emp_id not in (tb.member_agree or []):
            tb.member_agree = (tb.member_agree or []) + [emp_id]
        if emp_id in (tb.member_refuse or []):
            tb.member_refuse = [x for x in tb.member_refuse if x != emp_id]
    else:
        if emp_id not in (tb.member_refuse or []):
            tb.member_refuse = (tb.member_refuse or []) + [emp_id]
        if emp_id in (tb.member_agree or []):
            tb.member_agree = [x for x in tb.member_agree if x != emp_id]
    
    # 检查是否全员投票完成
    all_members = [m.get('id') for m in (tb.member_list or [])]
    voted = set(tb.member_agree or []) | set(tb.member_refuse or [])
    if all(m in voted for m in all_members):
        # 检查是否有人不参与
        if tb.member_refuse:
            tb.is_incomplete = True
        tb.status = 'pending'  # 进入待审核
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': '投票成功',
        'data': tb.to_dict()
    })


# ========== 积分兑换 ==========

@hr_v2_bp.route('/points/exchange', methods=['GET'])
@jwt_required_v2
def get_points_exchanges(current_user):
    """获取积分兑换记录"""
    emp_id = current_user.get('employee_id')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    query = PointsExchange.query
    if emp_id:
        query = query.filter_by(employee_id=emp_id)
    
    total = query.count()
    items = query.order_by(PointsExchange.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': 'success',
        'data': {
            'items': [i.to_dict() for i in items],
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })


@hr_v2_bp.route('/points/exchange', methods=['POST'])
@jwt_required_v2
def submit_points_exchange(current_user):
    """提交积分兑换"""
    data = request.get_json()
    
    emp_id = current_user.get('employee_id')
    if not emp_id:
        return jsonify({'code': 400, 'message': '未绑定员工账号'}), 400
    
    emp = Employee.query.get(emp_id)
    if not emp:
        return jsonify({'code': 404, 'message': '员工不存在'}), 404
    
    exchange_type = data.get('exchange_type', 'cash')
    
    # 获取积分账户
    account = EmployeePoints.query.filter_by(employee_id=emp_id).first()
    if not account:
        return jsonify({'code': 400, 'message': '积分账户不存在'}), 400
    
    if exchange_type == 'cash':
        # 现金兑换
        points_spent = data.get('points_spent', 0)
        if points_spent <= 0:
            return jsonify({'code': 400, 'message': '兑换积分必须大于0'}), 400
        
        if float(account.current_points) < points_spent:
            return jsonify({'code': 400, 'message': '可用积分不足'}), 400
        
        # 兑换比例：100积分 = 1元
        exchange_rate = 0.01
        cash_amount = points_spent * exchange_rate
        
        exchange = PointsExchange(
            employee_id=emp_id,
            employee_name=emp.name,
            exchange_type='cash',
            points_spent=points_spent,
            cash_amount=cash_amount,
            exchange_rate=exchange_rate,
            status='approved'
        )
        
    elif exchange_type == 'leave':
        # 带薪假兑换
        days_off = data.get('days_off', 1)
        points_required_per_day = 2000  # 10000积分=5天 → 2000/天
        points_spent = days_off * points_required_per_day
        
        if float(account.current_points) < points_spent:
            return jsonify({'code': 400, 'message': '可用积分不足'}), 400
        
        # 检查年内已用次数（每人每年限兑1次）
        year_start = datetime.utcnow().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        yearly_used = PointsExchange.query.filter(
            PointsExchange.employee_id == emp_id,
            PointsExchange.exchange_type == 'leave',
            PointsExchange.created_at >= year_start,
            PointsExchange.status == 'approved'
        ).count()
        
        if yearly_used >= 1:
            return jsonify({'code': 400, 'message': '每年仅限兑换1次带薪假'}), 400
        
        exchange = PointsExchange(
            employee_id=emp_id,
            employee_name=emp.name,
            exchange_type='leave',
            points_spent=points_spent,
            days_off=days_off,
            points_required_per_day=points_required_per_day,
            yearly_limit_used=yearly_used + 1,
            status='approved'
        )
    else:
        return jsonify({'code': 400, 'message': '不支持的兑换类型'}), 400
    
    # 扣减积分
    account.current_points = float(account.current_points) - exchange.points_spent
    account.total_used = float(account.total_used) + exchange.points_spent
    account.update_level()
    
    # 记录流水
    trans = PointsTransaction(
        employee_id=emp_id,
        type='use',
        points=-exchange.points_spent,
        balance_after=account.current_points,
        source_type='exchange',
        source_id=exchange.id,
        description=f'积分兑换（{"现金" if exchange_type == "cash" else "带薪假"}）',
        created_by=emp_id
    )
    
    db.session.add(exchange)
    db.session.add(trans)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'ok': True,
        'message': '兑换成功',
        'data': exchange.to_dict()
    })
