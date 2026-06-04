"""
认证系统 V2.0 模型
数据库：auth.db
支持：账号密码、微信、QQ 登录
"""
from app import db
from datetime import datetime
import json


class UserV2(db.Model):
    """用户表 V2 - 支持多登录方式"""
    __tablename__ = 'users_v2'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 基础信息
    username = db.Column(db.String(50), unique=True, nullable=False, comment='登录账号')
    nickname = db.Column(db.String(50), nullable=False, comment='用户昵称')
    phone = db.Column(db.String(20), unique=True, nullable=False, comment='手机号')
    email = db.Column(db.String(100), nullable=True, comment='邮箱')
    
    # 密码（统一密码策略：除admin外都是van654321）
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    password_changed_at = db.Column(db.DateTime, default=datetime.now, comment='密码修改时间')
    must_change_password = db.Column(db.Boolean, default=False, comment='首次登录必须修改密码')
    
    # 角色与权限
    role = db.Column(db.String(20), default='staff', comment='角色：super_admin/admin/manager/staff')
    store_id = db.Column(db.Integer, nullable=True, comment='所属门店ID')
    department_id = db.Column(db.Integer, nullable=True, comment='所属部门ID')
    employee_id = db.Column(db.Integer, nullable=True, comment='关联员工ID')
    
    # 账号状态
    status = db.Column(db.String(20), default='active', comment='状态：active/inactive/locked/resigned')
    login_fail_count = db.Column(db.Integer, default=0, comment='登录失败次数')
    locked_until = db.Column(db.DateTime, nullable=True, comment='锁定截止时间')
    
    # 微信登录
    wx_openid = db.Column(db.String(100), unique=True, nullable=True, comment='微信OpenID')
    wx_unionid = db.Column(db.String(100), nullable=True, comment='微信UnionID')
    wx_nickname = db.Column(db.String(100), nullable=True, comment='微信昵称')
    wx_avatar = db.Column(db.String(500), nullable=True, comment='微信头像')
    wx_bound_at = db.Column(db.DateTime, nullable=True, comment='微信绑定时间')
    
    # QQ登录
    qq_openid = db.Column(db.String(100), unique=True, nullable=True, comment='QQ OpenID')
    qq_nickname = db.Column(db.String(100), nullable=True, comment='QQ昵称')
    qq_avatar = db.Column(db.String(500), nullable=True, comment='QQ头像')
    qq_bound_at = db.Column(db.DateTime, nullable=True, comment='QQ绑定时间')
    
    # 登录记录
    last_login_at = db.Column(db.DateTime, nullable=True, comment='最后登录时间')
    last_login_ip = db.Column(db.String(50), nullable=True, comment='最后登录IP')
    last_login_method = db.Column(db.String(20), nullable=True, comment='最后登录方式：password/wechat/qq')
    
    # 安全
    two_factor_enabled = db.Column(db.Boolean, default=False, comment='是否开启双因素认证')
    two_factor_secret = db.Column(db.String(255), nullable=True, comment='双因素密钥')
    
    # 离职信息
    resigned_at = db.Column(db.DateTime, nullable=True, comment='离职时间')
    resigned_reason = db.Column(db.String(500), nullable=True, comment='离职原因')
    resigned_by = db.Column(db.Integer, nullable=True, comment='操作人ID')
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'phone': self.phone,
            'email': self.email,
            'role': self.role,
            'store_id': self.store_id,
            'department_id': self.department_id,
            'employee_id': self.employee_id,
            'status': self.status,
            'wx_bound': self.wx_openid is not None,
            'qq_bound': self.qq_openid is not None,
            'last_login_at': self.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_login_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
        if include_sensitive:
            data.update({
                'wx_nickname': self.wx_nickname,
                'wx_avatar': self.wx_avatar,
                'qq_nickname': self.qq_nickname,
                'qq_avatar': self.qq_avatar,
                'login_fail_count': self.login_fail_count,
                'locked_until': self.locked_until.strftime('%Y-%m-%d %H:%M:%S') if self.locked_until else None,
            })
        return data
    
    def is_locked(self):
        """检查账号是否被锁定"""
        if self.locked_until and self.locked_until > datetime.now():
            return True
        return False
    
    def can_reset_password(self, target_user):
        """检查是否有权限重置目标用户密码"""
        # 超级管理员可以重置所有人
        if self.role == 'super_admin':
            return True
        # 店长可以重置本店员工
        if self.role == 'manager' and target_user.store_id == self.store_id:
            return True
        return False


class PasswordResetToken(db.Model):
    """密码重置令牌"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_v2.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    token_type = db.Column(db.String(20), default='email', comment='类型：email/sms')
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    used_ip = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)


class LoginLog(db.Model):
    """登录日志"""
    __tablename__ = 'login_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_v2.id'), nullable=True)
    username = db.Column(db.String(50), nullable=True)
    login_method = db.Column(db.String(20), nullable=False, comment='登录方式')
    login_status = db.Column(db.String(20), nullable=False, comment='状态：success/failed')
    fail_reason = db.Column(db.String(255), nullable=True, comment='失败原因')
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    device_info = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)


class Store(db.Model):
    """门店/店铺 - 支持独立数据库架构"""
    __tablename__ = 'stores'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, comment='门店编码')
    name = db.Column(db.String(100), nullable=False, comment='门店名称')
    
    # 租户与数据库配置
    tenant_id = db.Column(db.String(32), unique=True, nullable=True, comment='租户ID')
    db_path = db.Column(db.String(255), nullable=True, comment='独立数据库路径')
    db_status = db.Column(db.String(20), default='pending', comment='数据库状态：pending/initialized/failed')
    
    # 地址信息
    province = db.Column(db.String(50), nullable=True, comment='省份')
    city = db.Column(db.String(50), nullable=True, comment='城市')
    district = db.Column(db.String(50), nullable=True, comment='区县')
    address = db.Column(db.String(255), nullable=True, comment='详细地址')
    
    # 联系信息
    phone = db.Column(db.String(20), nullable=True, comment='联系电话')
    manager_id = db.Column(db.Integer, nullable=True, comment='店长用户ID')
    
    # 运营信息
    opening_date = db.Column(db.Date, nullable=True, comment='开业日期')
    business_hours = db.Column(db.String(100), nullable=True, comment='营业时间')
    description = db.Column(db.Text, nullable=True, comment='分店描述')
    
    # 状态
    status = db.Column(db.String(20), default='active', comment='状态：active/inactive/deleted')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'tenant_id': self.tenant_id,
            'db_path': self.db_path,
            'db_status': self.db_status,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'address': self.address,
            'phone': self.phone,
            'manager_id': self.manager_id,
            'opening_date': self.opening_date.strftime('%Y-%m-%d') if self.opening_date else None,
            'business_hours': self.business_hours,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class DigitalAssetTransfer(db.Model):
    """数字资产转移记录 - 离职时客户资源归集"""
    __tablename__ = 'digital_asset_transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 离职员工
    from_user_id = db.Column(db.Integer, db.ForeignKey('users_v2.id'), nullable=False)
    from_employee_id = db.Column(db.Integer, nullable=False)
    
    # 接收人（可为空，表示归集到公海）
    to_user_id = db.Column(db.Integer, db.ForeignKey('users_v2.id'), nullable=True)
    to_employee_id = db.Column(db.Integer, nullable=True)
    
    # 资产类型
    asset_type = db.Column(db.String(50), nullable=False, comment='类型：customer/lead/contract/scheme')
    asset_id = db.Column(db.Integer, nullable=False, comment='资产ID')
    asset_name = db.Column(db.String(255), nullable=True, comment='资产名称（客户名等）')
    
    # 转移详情
    transfer_reason = db.Column(db.String(50), default='resignation', comment='原因：resignation/dismissal/transfer')
    transferred_by = db.Column(db.Integer, db.ForeignKey('users_v2.id'), nullable=False, comment='操作人')
    transferred_at = db.Column(db.DateTime, default=datetime.now)
    
    # 状态
    status = db.Column(db.String(20), default='completed', comment='状态：completed/pending/failed')
    notes = db.Column(db.Text, nullable=True, comment='备注')
    
    created_at = db.Column(db.DateTime, default=datetime.now)


class WechatAuth(db.Model):
    """微信认证信息"""
    __tablename__ = 'wechat_auths'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_v2.id'), nullable=True)
    openid = db.Column(db.String(100), unique=True, nullable=False)
    unionid = db.Column(db.String(100), nullable=True)
    session_key = db.Column(db.String(100), nullable=True)
    nickname = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    bound_at = db.Column(db.DateTime, default=datetime.now)
    last_used_at = db.Column(db.DateTime, default=datetime.now)


class QQAuth(db.Model):
    """QQ认证信息"""
    __tablename__ = 'qq_auths'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_v2.id'), nullable=True)
    openid = db.Column(db.String(100), unique=True, nullable=False)
    access_token = db.Column(db.String(255), nullable=True)
    nickname = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    bound_at = db.Column(db.DateTime, default=datetime.now)
    last_used_at = db.Column(db.DateTime, default=datetime.now)
