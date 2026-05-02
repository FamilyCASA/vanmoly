"""
人力资源管理系统 V2.0 API路由
所有模型统一在主数据库
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.hr import Department, Position, Employee
from app.models.hr_v2 import (
    EmployeeSalary, PerformanceReview, EmployeePoints, PointsTransaction,
    CareerPath, TrainingRecord, EmployeeWelfare
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
