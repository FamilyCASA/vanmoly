"""
预约量尺模块数据模型
"""
from datetime import datetime
from app import db


class Appointment(db.Model):
    """预约量尺表"""
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(50), nullable=False, comment='客户姓名')
    phone = db.Column(db.String(20), nullable=False, comment='手机号')
    house_address = db.Column(db.String(200), comment='房屋地址')
    house_type = db.Column(db.String(50), comment='户型')
    area = db.Column(db.String(50), comment='面积')
    budget = db.Column(db.String(50), comment='预算')
    appointment_date = db.Column(db.Date, comment='预约日期')
    appointment_time = db.Column(db.Time, comment='预约时间')
    status = db.Column(db.String(20), default='待确认', comment='状态')
    assigned_to = db.Column(db.Integer, comment='分配员工ID')
    remark = db.Column(db.Text, comment='备注')
    cancel_reason = db.Column(db.Text, comment='取消原因')
    ip_address = db.Column(db.String(50), comment='访客IP')
    tenant_id = db.Column(db.String(20), comment='租户ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 状态常量
    STATUS_PENDING = '待确认'
    STATUS_CONFIRMED = '已确认'
    STATUS_CANCELLED = '已取消'
    STATUS_COMPLETED = '已完成'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'phone': self.phone,
            'house_address': self.house_address,
            'house_type': self.house_type,
            'area': self.area,
            'budget': self.budget,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.isoformat() if self.appointment_time else None,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def confirm(self):
        """确认预约"""
        self.status = self.STATUS_CONFIRMED
        db.session.commit()

    def cancel(self, reason=None):
        """取消预约"""
        self.status = self.STATUS_CANCELLED
        if reason:
            self.cancel_reason = reason
        db.session.commit()

    def complete(self):
        """完成预约"""
        self.status = self.STATUS_COMPLETED
        db.session.commit()
