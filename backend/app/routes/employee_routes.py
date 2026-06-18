"""
员工管理模块 - API路由
V3.0 全新设计
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import (
    Employee, Department, Position, EmployeeContract, EmployeePerformance
)  # Employee/Department/Position 从 hr_v2 导入
from app.models.employee import (
    EMPLOYEE_STATUS, EMPLOYEE_ROLES, CONTRACT_TYPES
)
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime, date
from sqlalchemy import func

employee_bp = Blueprint('employee', __name__, url_prefix='/api/v3/employees')


# ========== 部门管理 ==========

@employee_bp.route('/departments', methods=['GET'])
@jwt_required_v2
def get_departments(current_user):
    """获取部门列表"""
    departments = Department.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_enabled=True
    ).order_by(Department.sort_order).all()

    return jsonify({
        'code': 200,
        'data': [d.to_dict() for d in departments]
    })


@employee_bp.route('/departments', methods=['POST'])
@jwt_required_v2
def create_department(current_user):
    """创建部门"""
    data = request.get_json()

    dept = Department(
        tenant_id=current_user.get('tenant_id', '0'),
        name=data['name'],
        code=data.get('code'),
        parent_id=data.get('parent_id'),
        manager_id=data.get('manager_id'),
        sort_order=data.get('sort_order', 0)
    )

    db.session.add(dept)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': dept.to_dict()
    })


@employee_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@jwt_required_v2
def update_department(dept_id, current_user):
    """更新部门"""
    data = request.get_json()
    dept = Department.query.get_or_404(dept_id)
    if 'name' in data: dept.name = data['name']
    if 'code' in data: dept.code = data['code']
    if 'parent_id' in data: dept.parent_id = data['parent_id']
    if 'manager_id' in data: dept.manager_id = data['manager_id']
    if 'sort_order' in data: dept.sort_order = data['sort_order']
    if 'is_enabled' in data: dept.is_enabled = data['is_enabled']
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': dept.to_dict()})


@employee_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@jwt_required_v2
def delete_department(dept_id, current_user):
    """删除部门（软删除，设置is_enabled=False）"""
    dept = Department.query.get_or_404(dept_id)
    dept.is_enabled = False
    db.session.commit()
    return jsonify({'code': 200, 'message': '已停用'})


# ========== 岗位管理 ==========

@employee_bp.route('/positions', methods=['GET'])
@jwt_required_v2
def get_positions(current_user):
    """获取岗位列表"""
    department_id = request.args.get('department_id', type=int)

    query = Position.query.filter_by(is_active=True)

    if department_id:
        query = query.filter_by(department_id=department_id)

    positions = query.order_by(Position.level).all()

    return jsonify({
        'code': 200,
        'data': [p.to_dict() for p in positions]
    })


@employee_bp.route('/positions', methods=['POST'])
@jwt_required_v2
def create_position(current_user):
    """创建岗位"""
    data = request.get_json()

    position = Position(
        name=data['name'],
        code=data.get('code'),
        department_id=data.get('department_id'),
        level=data.get('level', 1),
        description=data.get('description')
    )

    db.session.add(position)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': position.to_dict()
    })


@employee_bp.route('/positions/<int:pos_id>', methods=['PUT'])
@jwt_required_v2
def update_position(pos_id, current_user):
    """更新岗位"""
    data = request.get_json()
    pos = Position.query.get_or_404(pos_id)
    if 'name' in data: pos.name = data['name']
    if 'code' in data: pos.code = data['code']
    if 'department_id' in data: pos.department_id = data['department_id']
    if 'level' in data: pos.level = data['level']
    if 'description' in data: pos.description = data['description']
    if 'is_active' in data: pos.is_active = data['is_active']
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': pos.to_dict()})


@employee_bp.route('/positions/<int:pos_id>', methods=['DELETE'])
@jwt_required_v2
def delete_position(pos_id, current_user):
    """删除岗位（软删除，设置is_active=False）"""
    pos = Position.query.get_or_404(pos_id)
    pos.is_active = False
    db.session.commit()
    return jsonify({'code': 200, 'message': '已停用'})


# ========== 员工管理 ==========

@employee_bp.route('', methods=['GET'])
@jwt_required_v2
def get_employees(current_user):
    """获取员工列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    department_id = request.args.get('department_id', type=int)
    status = request.args.get('status')

    query = Employee.query

    if keyword:
        query = query.filter(
            db.or_(
                Employee.name.contains(keyword),
                Employee.phone.contains(keyword),
                Employee.employee_no.contains(keyword)
            )
        )

    if department_id:
        query = query.filter_by(department_id=department_id)
    if status:
        query = query.filter_by(status=status)
    role = request.args.get('role')
    if role:
        query = query.filter_by(role=role)

    query = query.order_by(Employee.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [e.to_dict() for e in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@employee_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
def get_employee(current_user, id):
    """获取员工详情"""
    employee = Employee.query.get_or_404(id)

    # 加载关联数据
    contracts = EmployeeContract.query.filter_by(
        employee_id=id
    ).order_by(EmployeeContract.created_at.desc()).all()

    # 本月业绩
    current_period = date.today().strftime('%Y-%m')
    performance = EmployeePerformance.query.filter_by(
        employee_id=id,
        period=current_period
    ).first()

    data = employee.to_dict(include_private=True)
    data['contracts'] = [c.to_dict() for c in contracts]
    data['performance'] = performance.to_dict() if performance else None

    return jsonify({
        'code': 200,
        'data': data
    })


@employee_bp.route('', methods=['POST'])
@jwt_required_v2
def create_employee(current_user):
    """创建员工"""
    data = request.get_json()

    # 检查工号是否重复
    if data.get('employee_no'):
        existing = Employee.query.filter_by(
            employee_no=data['employee_no'],
            is_deleted=False
        ).first()
        if existing:
            return jsonify({'code': 400, 'message': '工号已存在'}), 400

    from datetime import datetime
    entry_val = data.get('entry_date')
    entry_date_obj = None
    if entry_val and isinstance(entry_val, str):
        for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
            try:
                entry_date_obj = datetime.strptime(entry_val, fmt).date()
                break
            except ValueError:
                continue

    employee = Employee(
        tenant_id=current_user.get('tenant_id', '0'),
        name=data['name'],
        phone=data.get('phone'),
        email=data.get('email'),
        gender=data.get('gender'),
        employee_no=data.get('employee_no'),
        department_id=data.get('department_id'),
        position_id=data.get('position_id'),
        entry_date=entry_date_obj,
        job_level=data.get('job_level'),
        base_salary=data.get('base_salary'),
        role=data.get('role', 'employee'),
        status=data.get('status', 'active'),
        address=data.get('address'),
        emergency_contact=data.get('emergency_contact'),
        emergency_phone=data.get('emergency_phone'),
        remark=data.get('remark')
    )


    # 对外展示字段
    employee.title = data.get('title')
    employee.bio = data.get('bio')
    employee.showcase_photo = data.get('showcase_photo')

    db.session.add(employee)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': employee.to_dict()
    })


@employee_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_employee(current_user, id):
    """更新员工"""
    try:
        from datetime import datetime, date
        employee = Employee.query.get_or_404(id)
        data = request.get_json()

        # 日期字段映射：需要从字符串转成 date 对象
        date_fields = ['entry_date', 'birthday', 'probation_end_date', 'formal_date']

        fields = [
            'name', 'phone', 'email', 'gender', 'id_card',
            'employee_no', 'department_id', 'position_id',
            'job_level', 'base_salary', 'performance_ratio', 'role', 'status',
            'address', 'emergency_contact', 'emergency_phone', 'remark',
            'title', 'bio', 'showcase_photo'
        ]

        for field in fields:
            if field in data and data[field] is not None and data[field] != '':
                setattr(employee, field, data[field])

        for field in date_fields:
            if field in data and data[field]:
                val = data[field]
                if isinstance(val, str) and val:
                    # 支持 YYYY-MM-DD 或 YYYY/MM/DD
                    for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
                        try:
                            dt = datetime.strptime(val, fmt)
                            setattr(employee, field, dt.date())
                            break
                        except ValueError:
                            continue
                elif isinstance(val, date):
                    setattr(employee, field, val)

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': employee.to_dict()
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'code': 500, 'message': str(e)})


@employee_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_employee(current_user, id):
    """删除员工（软删除）"""
    employee = Employee.query.get_or_404(id)
    employee.is_deleted = True
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


# ========== 合同管理 ==========

@employee_bp.route('/<int:employee_id>/contracts', methods=['GET'])
@jwt_required_v2
def get_contracts(current_user, employee_id):
    """获取员工合同列表"""
    contracts = EmployeeContract.query.filter_by(
        employee_id=employee_id
    ).order_by(EmployeeContract.created_at.desc()).all()

    return jsonify({
        'code': 200,
        'data': [c.to_dict() for c in contracts]
    })


@employee_bp.route('/<int:employee_id>/contracts', methods=['POST'])
@jwt_required_v2
def create_contract(current_user, employee_id):
    """创建合同"""
    data = request.get_json()

    contract = EmployeeContract(
        employee_id=employee_id,
        contract_no=data.get('contract_no'),
        contract_type=data['contract_type'],
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        signed_date=data.get('signed_date'),
        salary=data.get('salary'),
        probation_months=data.get('probation_months'),
        file_url=data.get('file_url'),
        remark=data.get('remark')
    )

    db.session.add(contract)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': contract.to_dict()
    })


# ========== 业绩管理 ==========

@employee_bp.route('/<int:employee_id>/performance', methods=['GET'])
@jwt_required_v2
def get_performance(current_user, employee_id):
    """获取员工业绩"""
    period = request.args.get('period')

    query = EmployeePerformance.query.filter_by(employee_id=employee_id)

    if period:
        query = query.filter_by(period=period)

    records = query.order_by(EmployeePerformance.period.desc()).all()

    return jsonify({
        'code': 200,
        'data': [r.to_dict() for r in records]
    })


@employee_bp.route('/<int:employee_id>/performance', methods=['POST'])
@jwt_required_v2
def create_performance(current_user, employee_id):
    """创建业绩记录"""
    data = request.get_json()

    # 检查是否已存在
    existing = EmployeePerformance.query.filter_by(
        employee_id=employee_id,
        period=data['period']
    ).first()

    if existing:
        return jsonify({'code': 400, 'message': '该周期业绩已存在'}), 400

    performance = EmployeePerformance(
        employee_id=employee_id,
        period=data['period'],
        target_amount=data.get('target_amount', 0),
        actual_amount=data.get('actual_amount', 0),
        commission=data.get('commission', 0),
        bonus=data.get('bonus', 0),
        order_count=data.get('order_count', 0),
        customer_count=data.get('customer_count', 0)
    )

    db.session.add(performance)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': performance.to_dict()
    })


# ========== 统计报表 ==========

@employee_bp.route('/statistics', methods=['GET'])
@jwt_required_v2
def get_statistics(current_user):
    """获取员工统计"""
    tenant_id = current_user.get('tenant_id', '0')

    # 总数
    total = Employee.query.filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).count()

    # 按状态统计
    status_stats = db.session.query(
        Employee.status,
        func.count(Employee.id)
    ).filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).group_by(Employee.status).all()

    # 按部门统计
    dept_stats = db.session.query(
        Department.name,
        func.count(Employee.id)
    ).join(Employee, Employee.department_id == Department.id).filter(
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False
    ).group_by(Department.name).all()

    # 本月新增
    current_month = date.today().replace(day=1)
    new_this_month = Employee.query.filter(
        Employee.tenant_id == tenant_id,
        Employee.is_deleted == False,
        Employee.created_at >= current_month
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'total': total,
            'by_status': {s: c for s, c in status_stats},
            'by_department': {d: c for d, c in dept_stats},
            'new_this_month': new_this_month
        }
    })


# ========== 选项数据 ==========

@employee_bp.route('/options', methods=['GET'])
@jwt_required_v2
def get_options(current_user):
    """获取员工相关选项"""
    return jsonify({
        'code': 200,
        'data': {
            'status_list': [{'value': v, 'label': l} for v, l in EMPLOYEE_STATUS],
            'roles': [{'value': v, 'label': l} for v, l in EMPLOYEE_ROLES],
            'contract_types': [{'value': v, 'label': l} for v, l in CONTRACT_TYPES],
        }
    })
