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
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime

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
    
    emp = Employee(
        employee_no=employee_no,
        name=data['name'],
        gender=data.get('gender'),
        phone=data.get('phone'),
        email=data.get('email'),
        department_id=data.get('department_id'),
        position_id=data.get('position_id'),
        job_level=data.get('job_level', 1),
        entry_date=data.get('entry_date'),
        is_key_talent=data.get('is_key_talent', False),
        talent_level=data.get('talent_level', 'C')
    )
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


@hr_v2_bp.route('/employees/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_employee(current_user, id):
    """更新员工"""
    emp = Employee.query.get_or_404(id)
    data = request.get_json()
    
    emp.name = data.get('name', emp.name)
    emp.phone = data.get('phone', emp.phone)
    emp.email = data.get('email', emp.email)
    emp.department_id = data.get('department_id', emp.department_id)
    emp.position_id = data.get('position_id', emp.position_id)
    emp.job_level = data.get('job_level', emp.job_level)
    emp.is_key_talent = data.get('is_key_talent', emp.is_key_talent)
    emp.talent_level = data.get('talent_level', emp.talent_level)
    
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
