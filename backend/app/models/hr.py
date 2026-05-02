# -*- coding: utf-8 -*-
"""
员工管理模块 - 唯一版本（V3.0 最终版）

Department/Position/Employee 和基础模型（EmployeeContract/EmployeePerformance）
统一在此文件。HR扩展模型（薪资/绩效/积分等）见 hr_v2.py。
所有表都在主数据库（无 __bind_key__）。
"""
from datetime import datetime
from app import db


class Department(db.Model):
    """部门"""
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    name = db.Column(db.String(50), nullable=False, comment='部门名称')
    code = db.Column(db.String(20), unique=True, comment='部门编码')
    parent_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    manager_id = db.Column(db.Integer, comment='部门负责人ID')
    sort_order = db.Column(db.Integer, default=0)
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    parent = db.relationship('Department', remote_side=[id], backref='children')
    positions = db.relationship('Position', backref='department', lazy='dynamic')
    employees = db.relationship('Employee', backref='department', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'manager_id': self.manager_id,
            'sort_order': self.sort_order,
            'is_enabled': self.is_enabled,
            'is_active': self.is_active,
        }


class Position(db.Model):
    """职位"""
    __tablename__ = 'position'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, comment='职位名称')
    code = db.Column(db.String(20), unique=True, comment='职位编码')
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    level = db.Column(db.Integer, default=1, comment='职级')
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employees = db.relationship('Employee', backref='position', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'department_id': self.department_id,
            'level': self.level,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
        }


class Employee(db.Model):
    """员工"""
    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(32), comment='租户ID')
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    phone = db.Column(db.String(20), unique=True, comment='手机号')
    email = db.Column(db.String(100), comment='邮箱')
    gender = db.Column(db.String(10), comment='性别')
    id_card = db.Column(db.String(20), comment='身份证')
    birthday = db.Column(db.Date, comment='生日')
    employee_no = db.Column(db.String(20), comment='工号')

    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=True)

    # 入职相关
    entry_date = db.Column(db.Date, comment='入职日期')
    probation_end_date = db.Column(db.Date, comment='试用期结束日期')
    formal_date = db.Column(db.Date, comment='转正日期')
    join_date = db.Column(db.DateTime, comment='入职时间')
    leave_date = db.Column(db.DateTime, comment='离职时间')
    resignation_date = db.Column(db.DateTime, comment='辞职时间')

    # 职位相关
    job_level = db.Column(db.String(20), comment='职级')
    base_salary = db.Column(db.Numeric(10, 2), default=0, comment='基本工资')
    performance_ratio = db.Column(db.Numeric(3, 2), default=0, comment='绩效比例')

    # 登录相关
    username = db.Column(db.String(50), unique=True, comment='用户名')
    password_hash = db.Column(db.String(255), comment='密码哈希')
    role = db.Column(db.String(20), default='employee', comment='角色')

    # 状态
    status = db.Column(db.String(20), default='active', comment='状态')
    avatar = db.Column(db.String(255), comment='头像')

    # 其他信息
    address = db.Column(db.String(255), comment='地址')
    emergency_contact = db.Column(db.String(50), comment='紧急联系人')
    emergency_phone = db.Column(db.String(20), comment='紧急联系电话')
    remark = db.Column(db.Text, comment='备注')

    # 个人简介
    title = db.Column(db.String(100), comment='职称/头衔(如全案规划师)')
    bio = db.Column(db.Text, comment='个人简介')

    # 系统字段
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    store_id = db.Column(db.Integer, comment='门店ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_private=False):
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'gender': self.gender,
            'employee_no': self.employee_no,
            'department_id': self.department_id,
            'position_id': self.position_id,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'job_level': self.job_level,
            'status': self.status,
            'role': self.role,
            'avatar': self.avatar,
            'title': self.title,
            'bio': self.bio,
            'username': self.username,
            'department_name': self.department.name if self.department else None,
            'position_name': self.position.name if self.position else None,
        }
        if include_private:
            data.update({
                'id_card': self.id_card,
                'birthday': self.birthday.isoformat() if self.birthday else None,
                'base_salary': float(self.base_salary) if self.base_salary else 0,
                'address': self.address,
                'emergency_contact': self.emergency_contact,
                'emergency_phone': self.emergency_phone,
                'remark': self.remark,
                'store_id': self.store_id,
            })
        return data


class EmployeeContract(db.Model):
    """员工合同"""
    __tablename__ = 'employee_contract'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    contract_no = db.Column(db.String(50), comment='合同编号')
    contract_type = db.Column(db.String(20), comment='合同类型')
    start_date = db.Column(db.Date, comment='开始日期')
    end_date = db.Column(db.Date, comment='结束日期')
    signed_date = db.Column(db.Date, comment='签署日期')
    salary = db.Column(db.Numeric(10, 2), comment='约定薪资')
    probation_months = db.Column(db.Integer, comment='试用期月数')
    file_url = db.Column(db.String(255), comment='合同文件')
    remark = db.Column(db.Text, comment='备注')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'contract_no': self.contract_no,
            'contract_type': self.contract_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'salary': float(self.salary) if self.salary else None,
            'is_active': self.is_active,
        }


class EmployeePerformance(db.Model):
    """员工业绩记录"""
    __tablename__ = 'employee_performance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    period = db.Column(db.String(20), comment='统计周期')
    target_amount = db.Column(db.Numeric(12, 2), default=0, comment='目标业绩')
    actual_amount = db.Column(db.Numeric(12, 2), default=0, comment='实际业绩')
    commission = db.Column(db.Numeric(10, 2), default=0, comment='提成')
    bonus = db.Column(db.Numeric(10, 2), default=0, comment='奖金')
    order_count = db.Column(db.Integer, default=0, comment='订单数')
    customer_count = db.Column(db.Integer, default=0, comment='客户数')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'period': self.period,
            'target_amount': float(self.target_amount) if self.target_amount else 0,
            'actual_amount': float(self.actual_amount) if self.actual_amount else 0,
            'commission': float(self.commission) if self.commission else 0,
            'bonus': float(self.bonus) if self.bonus else 0,
            'order_count': self.order_count,
            'customer_count': self.customer_count,
        }
