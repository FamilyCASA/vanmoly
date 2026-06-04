"""
优惠券模块数据模型
"""
from datetime import datetime
from app import db


class Coupon(db.Model):
    """优惠券表"""
    __tablename__ = 'coupon'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='优惠券名称')
    type = db.Column(db.String(20), comment='类型')
    value = db.Column(db.Numeric(10, 2), comment='优惠金额')
    discount_percent = db.Column(db.Integer, comment='折扣百分比')
    min_amount = db.Column(db.Numeric(10, 2), comment='最低消费门槛')
    valid_from = db.Column(db.Date, comment='有效期开始')
    valid_to = db.Column(db.Date, comment='有效期结束')
    quantity = db.Column(db.Integer, comment='发放数量')
    used_count = db.Column(db.Integer, default=0, comment='已使用数量')
    status = db.Column(db.String(20), default='未发布', comment='状态')
    image_url = db.Column(db.String(500), comment='海报图片')
    description = db.Column(db.Text, comment='使用说明')
    tenant_id = db.Column(db.String(20), comment='租户ID')
    created_by = db.Column(db.Integer, comment='创建人ID')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 类型常量
    TYPE_VISIT = '到店礼'
    TYPE_DEPOSIT = '定金抵扣'
    TYPE_COMPLETION = '竣工礼'

    # 状态常量
    STATUS_DRAFT = '未发布'
    STATUS_ACTIVE = '进行中'
    STATUS_ENDED = '已结束'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'value': float(self.value) if self.value else None,
            'discount_percent': self.discount_percent,
            'min_amount': float(self.min_amount) if self.min_amount else None,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_to': self.valid_to.isoformat() if self.valid_to else None,
            'quantity': self.quantity,
            'used_count': self.used_count,
            'status': self.status,
            'image_url': self.image_url,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def is_valid(self):
        """检查优惠券是否有效"""
        from datetime import date
        if self.status != self.STATUS_ACTIVE:
            return False
        if self.valid_to and self.valid_to < date.today():
            return False
        if self.quantity and self.used_count >= self.quantity:
            return False
        return True


class CouponClaim(db.Model):
    """优惠券领取记录表"""
    __tablename__ = 'coupon_claim'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id'), nullable=False)
    phone = db.Column(db.String(20), nullable=False, comment='领取手机号')
    claim_code = db.Column(db.String(50), unique=True, comment='核销码')
    claimed_at = db.Column(db.DateTime, default=datetime.utcnow, comment='领取时间')
    used_at = db.Column(db.DateTime, comment='使用时间')
    used_by = db.Column(db.Integer, db.ForeignKey('employee.id'), comment='核销员工ID')
    status = db.Column(db.String(20), default='未使用', comment='状态')

    # 关联关系
    coupon = db.relationship('Coupon', backref='claims')

    # 状态常量
    STATUS_UNUSED = '未使用'
    STATUS_USED = '已使用'
    STATUS_EXPIRED = '已过期'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'coupon_id': self.coupon_id,
            'phone': self.phone,
            'claim_code': self.claim_code,
            'claimed_at': self.claimed_at.isoformat() if self.claimed_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'status': self.status,
        }

    def redeem(self, employee_id=None):
        """核销优惠券"""
        self.status = self.STATUS_USED
        self.used_at = datetime.utcnow()
        if employee_id:
            self.used_by = employee_id
        
        # 更新优惠券使用数量
        if self.coupon:
            self.coupon.used_count += 1
        
        db.session.commit()
