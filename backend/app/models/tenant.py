"""
Tenant/TenantUser 模型 — 多门店隔离核心
"""
from datetime import datetime
from app import db


class Tenant(db.Model):
    """租户/门店组织"""
    __tablename__ = 'tenant'

    id = db.Column(db.String(50), primary_key=True)  # 如 'hq', 'store_001'
    name = db.Column(db.String(100), nullable=False, comment='租户/门店名称')
    type = db.Column(db.String(20), default='store', comment='类型: hq=总部, store=门店')
    parent_id = db.Column(db.String(50), comment='父级租户ID（门店的父级是总部）')

    # 门店配置
    store_code = db.Column(db.String(50), unique=True, comment='门店编码')
    address = db.Column(db.String(255), comment='门店地址')
    phone = db.Column(db.String(20), comment='联系电话')
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'parent_id': self.parent_id,
            'store_code': self.store_code,
            'address': self.address,
            'phone': self.phone,
            'is_active': self.is_active,
        }


class TenantUser(db.Model):
    """租户-用户关联（总部员工账号体系）"""
    __tablename__ = 'tenant_user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.String(50), db.ForeignKey('tenant.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    
    role = db.Column(db.String(20), default='employee', comment='角色: admin/manager/employee')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'employee_id': self.employee_id,
            'role': self.role,
            'is_active': self.is_active,
        }