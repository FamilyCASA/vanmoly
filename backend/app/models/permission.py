# -*- coding: utf-8 -*-
"""
细粒度权限模型
"""
from datetime import datetime
from app import db
from app.models.auth_v2 import UserV2
from app.models.hr import Employee


def _datetime_value(value):
    return value.strftime('%Y-%m-%d %H:%M:%S') if value else None


class PermissionAssignment(db.Model):
    """给员工/账号分配某个范围内的操作权限"""
    __tablename__ = 'permission_assignment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_v2.id'), nullable=True, comment='授权账号')
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True, comment='授权员工')
    permission_key = db.Column(db.String(100), nullable=False, index=True, comment='权限键')
    scope_type = db.Column(db.String(30), default='global', index=True, comment='范围类型')
    scope_id = db.Column(db.Integer, nullable=True, index=True, comment='范围ID')
    granted_by = db.Column(db.Integer, nullable=True, comment='授权人用户ID')
    reason = db.Column(db.String(255), comment='授权原因')
    is_active = db.Column(db.Boolean, default=True, index=True, comment='是否启用')
    expires_at = db.Column(db.DateTime, nullable=True, comment='过期时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('UserV2')
    employee = db.relationship('Employee')

    def is_effective(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else None,
            'permission_key': self.permission_key,
            'scope_type': self.scope_type,
            'scope_id': self.scope_id,
            'granted_by': self.granted_by,
            'reason': self.reason,
            'is_active': self.is_active,
            'expires_at': _datetime_value(self.expires_at),
            'created_at': _datetime_value(self.created_at),
            'updated_at': _datetime_value(self.updated_at),
        }


class PermissionAuditLog(db.Model):
    """权限变更审计"""
    __tablename__ = 'permission_audit_log'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    operator_user_id = db.Column(db.Integer, nullable=True, comment='操作人')
    target_user_id = db.Column(db.Integer, nullable=True, comment='目标账号')
    target_employee_id = db.Column(db.Integer, nullable=True, comment='目标员工')
    action = db.Column(db.String(30), nullable=False, comment='操作')
    permission_key = db.Column(db.String(100), comment='权限键')
    scope_type = db.Column(db.String(30), comment='范围类型')
    scope_id = db.Column(db.Integer, nullable=True, comment='范围ID')
    detail = db.Column(db.Text, comment='详情')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'operator_user_id': self.operator_user_id,
            'target_user_id': self.target_user_id,
            'target_employee_id': self.target_employee_id,
            'action': self.action,
            'permission_key': self.permission_key,
            'scope_type': self.scope_type,
            'scope_id': self.scope_id,
            'detail': self.detail,
            'created_at': _datetime_value(self.created_at),
        }
