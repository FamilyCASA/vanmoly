"""
认证系统 V2.0 API路由
支持：账号密码、微信、QQ登录
统一密码策略、密码重置、离职资产归集
"""
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.auth_v2 import UserV2, PasswordResetToken, LoginLog, Store, DigitalAssetTransfer, WechatAuth, QQAuth
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
import re
from functools import wraps

auth_v2_bp = Blueprint('auth_v2', __name__)

# 统一密码（除admin外）
DEFAULT_PASSWORD = 'van654321'
MAX_LOGIN_FAILS = 5
LOCK_DURATION_MINUTES = 30


def generate_token(user_id, role):
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_reset_token():
    """生成重置令牌"""
    return secrets.token_urlsafe(32)


def jwt_required_v2(f):
    """JWT验证装饰器 V2"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'code': 401, 'message': 'Token格式错误'}), 401
        
        if not token:
            return jsonify({'code': 401, 'message': '缺少认证令牌'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'code': 401, 'message': '令牌无效或已过期'}), 401
        
        # 检查用户状态
        user = UserV2.query.get(payload['user_id'])
        if not user:
            return jsonify({'code': 401, 'message': '用户不存在'}), 401
        if user.status == 'resigned':
            return jsonify({'code': 403, 'message': '账号已离职，无法访问'}), 403
        if user.status == 'locked' or user.is_locked():
            return jsonify({'code': 403, 'message': '账号已被锁定'}), 403
        if user.status != 'active':
            return jsonify({'code': 403, 'message': '账号未激活'}), 403
        
        # Build current_user dict for route handlers
        current_user = {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'role': user.role,
            'tenant_id': getattr(user, 'tenant_id', '0'),
            'store_id': getattr(user, 'store_id', None),
            'department_id': getattr(user, 'department_id', None),
            'phone': getattr(user, 'phone', None),
            'email': getattr(user, 'email', None),
            'status': user.status,
        }
        request.current_user = current_user
        return f(current_user, *args, **kwargs)
    return decorated


def get_client_ip():
    """获取客户端IP"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr


def log_login(user_id, username, method, status, fail_reason=None):
    """记录登录日志"""
    log = LoginLog(
        user_id=user_id,
        username=username,
        login_method=method,
        login_status=status,
        fail_reason=fail_reason,
        ip_address=get_client_ip(),
        user_agent=request.headers.get('User-Agent'),
        device_info=request.headers.get('X-Device-Info')
    )
    db.session.add(log)
    db.session.commit()


# ========== 登录接口 ==========

@auth_v2_bp.route('/login', methods=['POST'])
def login():
    """账号密码登录 - 支持昵称或手机号"""
    data = request.get_json()
    identifier = data.get('identifier', '').strip()  # 昵称或手机号
    password = data.get('password', '')
    
    if not identifier or not password:
        return jsonify({'code': 400, 'message': '请输入账号和密码'}), 400
    
    # 查找用户（通过昵称或手机号）
    user = UserV2.query.filter(
        db.or_(
            UserV2.nickname == identifier,
            UserV2.phone == identifier,
            UserV2.username == identifier
        )
    ).first()
    
    if not user:
        log_login(None, identifier, 'password', 'failed', '用户不存在')
        return jsonify({'code': 401, 'message': '账号或密码错误'}), 401
    
    # 检查账号状态
    if user.status == 'resigned':
        log_login(user.id, user.username, 'password', 'failed', '账号已离职')
        return jsonify({'code': 403, 'message': '该账号已离职，无法登录'}), 403
    
    if user.is_locked():
        remaining = int((user.locked_until - datetime.now()).total_seconds() / 60)
        log_login(user.id, user.username, 'password', 'failed', f'账号锁定，剩余{remaining}分钟')
        return jsonify({
            'code': 403, 
            'message': f'账号已锁定，请{remaining}分钟后重试',
            'locked_until': user.locked_until.strftime('%Y-%m-%d %H:%M:%S')
        }), 403
    
    # 验证密码
    password_hash = hash_password(password)
    if password_hash != user.password_hash:
        # 增加失败次数
        user.login_fail_count += 1
        if user.login_fail_count >= MAX_LOGIN_FAILS:
            user.locked_until = datetime.now() + timedelta(minutes=LOCK_DURATION_MINUTES)
            db.session.commit()
            log_login(user.id, user.username, 'password', 'failed', f'密码错误，账号锁定{LOCK_DURATION_MINUTES}分钟')
            return jsonify({
                'code': 403,
                'message': f'密码错误次数过多，账号已锁定{LOCK_DURATION_MINUTES}分钟',
                'locked': True
            }), 403
        db.session.commit()
        remaining = MAX_LOGIN_FAILS - user.login_fail_count
        log_login(user.id, user.username, 'password', 'failed', '密码错误')
        return jsonify({
            'code': 401,
            'message': f'账号或密码错误，还剩{remaining}次机会',
            'remaining_attempts': remaining
        }), 401
    
    # 首次登录必须修改密码（非admin）
    if user.username != 'admin' and user.must_change_password:
        token = generate_token(user.id, user.role)
        log_login(user.id, user.username, 'password', 'success')
        return jsonify({
            'code': 200,
            'data': {
                'token': token,
                'user': user.to_dict(),
                'must_change_password': True,
                'message': '首次登录，请修改密码'
            },
            'message': '登录成功，请修改初始密码'
        })
    
    # 登录成功
    user.login_fail_count = 0
    user.locked_until = None
    user.last_login_at = datetime.now()
    user.last_login_ip = get_client_ip()
    user.last_login_method = 'password'
    db.session.commit()
    
    token = generate_token(user.id, user.role)
    log_login(user.id, user.username, 'password', 'success')
    
    return jsonify({
        'code': 200,
        'data': {
            'token': token,
            'user': user.to_dict(),
            'must_change_password': False
        },
        'message': '登录成功'
    })


@auth_v2_bp.route('/login/wechat', methods=['POST'])
def login_wechat():
    """微信登录"""
    data = request.get_json()
    code = data.get('code')  # 微信授权码
    
    if not code:
        return jsonify({'code': 400, 'message': '缺少微信授权码'}), 400
    
    # TODO: 调用微信接口换取openid
    # 这里使用模拟数据，实际需接入微信SDK
    wx_openid = f"wx_mock_{code}"
    
    # 查找已绑定的用户
    user = UserV2.query.filter_by(wx_openid=wx_openid, status='active').first()
    
    if not user:
        return jsonify({
            'code': 404,
            'message': '该微信未绑定账号，请先绑定',
            'need_bind': True,
            'wx_openid': wx_openid
        }), 404
    
    # 更新登录信息
    user.last_login_at = datetime.now()
    user.last_login_ip = get_client_ip()
    user.last_login_method = 'wechat'
    db.session.commit()
    
    token = generate_token(user.id, user.role)
    log_login(user.id, user.username, 'wechat', 'success')
    
    return jsonify({
        'code': 200,
        'data': {
            'token': token,
            'user': user.to_dict()
        },
        'message': '微信登录成功'
    })


@auth_v2_bp.route('/login/qq', methods=['POST'])
def login_qq():
    """QQ登录"""
    data = request.get_json()
    code = data.get('code')  # QQ授权码
    
    if not code:
        return jsonify({'code': 400, 'message': '缺少QQ授权码'}), 400
    
    # TODO: 调用QQ接口换取openid
    qq_openid = f"qq_mock_{code}"
    
    user = UserV2.query.filter_by(qq_openid=qq_openid, status='active').first()
    
    if not user:
        return jsonify({
            'code': 404,
            'message': '该QQ未绑定账号，请先绑定',
            'need_bind': True,
            'qq_openid': qq_openid
        }), 404
    
    user.last_login_at = datetime.now()
    user.last_login_ip = get_client_ip()
    user.last_login_method = 'qq'
    db.session.commit()
    
    token = generate_token(user.id, user.role)
    log_login(user.id, user.username, 'qq', 'success')
    
    return jsonify({
        'code': 200,
        'data': {
            'token': token,
            'user': user.to_dict()
        },
        'message': 'QQ登录成功'
    })


# ========== 注册与绑定 ==========

@auth_v2_bp.route('/register', methods=['POST'])
@jwt_required_v2
def register_user(current_user):
    """创建用户（需管理员权限）"""
    current_user = request.current_user
    if current_user.role not in ['super_admin', 'admin', 'manager']:
        return jsonify({'code': 403, 'message': '无权限创建用户'}), 403
    
    data = request.get_json()
    username = data.get('username', '').strip()
    nickname = data.get('nickname', '').strip()
    phone = data.get('phone', '').strip()
    role = data.get('role', 'staff')
    store_id = data.get('store_id')
    
    # 验证必填
    if not nickname or not phone:
        return jsonify({'code': 400, 'message': '昵称和手机号必填'}), 400
    
    # 验证手机号格式
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify({'code': 400, 'message': '手机号格式错误'}), 400
    
    # 检查重复
    if UserV2.query.filter_by(phone=phone).first():
        return jsonify({'code': 409, 'message': '该手机号已注册'}), 409
    
    if UserV2.query.filter_by(nickname=nickname).first():
        return jsonify({'code': 409, 'message': '该昵称已被使用'}), 409
    
    # 自动生成用户名
    if not username:
        username = f"vm{phone[-8:]}"
    
    if UserV2.query.filter_by(username=username).first():
        return jsonify({'code': 409, 'message': '该用户名已存在'}), 409
    
    # 创建用户（使用默认密码）
    user = UserV2(
        username=username,
        nickname=nickname,
        phone=phone,
        password_hash=hash_password(DEFAULT_PASSWORD),
        role=role,
        store_id=store_id,
        must_change_password=True  # 首次登录必须改密码
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': user.to_dict(),
        'message': f'用户创建成功，初始密码：{DEFAULT_PASSWORD}'
    })


@auth_v2_bp.route('/bind/wechat', methods=['POST'])
@jwt_required_v2
def bind_wechat(current_user):
    """绑定微信"""
    user = request.current_user
    data = request.get_json()
    code = data.get('code')
    
    # TODO: 调用微信接口
    wx_openid = f"wx_bind_{code}"
    
    # 检查是否已被其他账号绑定
    existing = UserV2.query.filter_by(wx_openid=wx_openid).first()
    if existing and existing.id != user.id:
        return jsonify({'code': 409, 'message': '该微信已绑定其他账号'}), 409
    
    user.wx_openid = wx_openid
    user.wx_bound_at = datetime.now()
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '微信绑定成功'})


@auth_v2_bp.route('/bind/qq', methods=['POST'])
@jwt_required_v2
def bind_qq(current_user):
    """绑定QQ"""
    user = request.current_user
    data = request.get_json()
    code = data.get('code')
    
    qq_openid = f"qq_bind_{code}"
    
    existing = UserV2.query.filter_by(qq_openid=qq_openid).first()
    if existing and existing.id != user.id:
        return jsonify({'code': 409, 'message': '该QQ已绑定其他账号'}), 409
    
    user.qq_openid = qq_openid
    user.qq_bound_at = datetime.now()
    db.session.commit()
    
    return jsonify({'code': 200, 'message': 'QQ绑定成功'})


# ========== 密码管理 ==========

@auth_v2_bp.route('/password/change', methods=['POST'])
@jwt_required_v2
def change_password(current_user):
    """修改密码"""
    user = request.current_user
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if not old_password or not new_password:
        return jsonify({'code': 400, 'message': '请输入原密码和新密码'}), 400
    
    # 验证原密码
    if hash_password(old_password) != user.password_hash:
        return jsonify({'code': 401, 'message': '原密码错误'}), 401
    
    # 验证新密码强度
    if len(new_password) < 6:
        return jsonify({'code': 400, 'message': '新密码至少6位'}), 400
    
    # 不能是默认密码
    if new_password == DEFAULT_PASSWORD and user.username != 'admin':
        return jsonify({'code': 400, 'message': '不能使用默认密码'}), 400
    
    user.password_hash = hash_password(new_password)
    user.password_changed_at = datetime.now()
    user.must_change_password = False
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '密码修改成功'})


@auth_v2_bp.route('/password/reset-request', methods=['POST'])
def request_password_reset():
    """请求重置密码（忘记密码）"""
    data = request.get_json()
    phone = data.get('phone', '').strip()
    
    if not phone:
        return jsonify({'code': 400, 'message': '请输入手机号'}), 400
    
    user = UserV2.query.filter_by(phone=phone).first()
    if not user:
        # 不暴露用户是否存在
        return jsonify({'code': 200, 'message': '如果该手机号已注册，将收到重置验证码'})
    
    # TODO: 发送短信验证码
    # 这里生成一个模拟验证码
    reset_code = "123456"
    
    # 创建重置令牌
    token = generate_reset_token()
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        token_type='sms',
        expires_at=datetime.now() + timedelta(minutes=10)
    )
    db.session.add(reset_token)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': {
            'reset_token': token,
            'expires_in': 600  # 10分钟
        },
        'message': '验证码已发送（演示模式：123456）'
    })


@auth_v2_bp.route('/password/reset', methods=['POST'])
def reset_password():
    """重置密码（使用验证码）"""
    data = request.get_json()
    token = data.get('token', '')
    code = data.get('code', '')
    new_password = data.get('new_password', '')
    
    if not token or not code or not new_password:
        return jsonify({'code': 400, 'message': '缺少必要参数'}), 400
    
    # 验证令牌
    reset_token = PasswordResetToken.query.filter_by(
        token=token,
        used_at=None
    ).first()
    
    if not reset_token or reset_token.expires_at < datetime.now():
        return jsonify({'code': 400, 'message': '验证码已过期，请重新获取'}), 400
    
    # TODO: 验证短信验证码
    if code != '123456':
        return jsonify({'code': 400, 'message': '验证码错误'}), 400
    
    # 验证新密码
    if len(new_password) < 6:
        return jsonify({'code': 400, 'message': '新密码至少6位'}), 400
    
    user = UserV2.query.get(reset_token.user_id)
    user.password_hash = hash_password(new_password)
    user.password_changed_at = datetime.now()
    user.must_change_password = False
    user.login_fail_count = 0
    user.locked_until = None
    
    # 标记令牌已使用
    reset_token.used_at = datetime.now()
    reset_token.used_ip = get_client_ip()
    
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '密码重置成功，请使用新密码登录'})


@auth_v2_bp.route('/password/admin-reset', methods=['POST'])
@jwt_required_v2
def admin_reset_password(current_user):
    """管理员重置他人密码"""
    current_user = request.current_user
    data = request.get_json()
    target_user_id = data.get('user_id')
    
    if not target_user_id:
        return jsonify({'code': 400, 'message': '请指定要重置密码的用户'}), 400
    
    target_user = UserV2.query.get_or_404(target_user_id)
    
    # 权限检查
    if not current_user.can_reset_password(target_user):
        return jsonify({'code': 403, 'message': '无权限重置该用户密码'}), 403
    
    # 重置为默认密码
    target_user.password_hash = hash_password(DEFAULT_PASSWORD)
    target_user.must_change_password = True
    target_user.login_fail_count = 0
    target_user.locked_until = None
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': {
            'user_id': target_user.id,
            'username': target_user.username,
            'default_password': DEFAULT_PASSWORD
        },
        'message': f'密码已重置为：{DEFAULT_PASSWORD}，用户首次登录需修改密码'
    })


# ========== 离职处理 ==========

@auth_v2_bp.route('/users/<int:user_id>/resign', methods=['POST'])
@jwt_required_v2
def resign_user(current_user, user_id):
    """员工离职/辞退处理 - 账户回收+资产归集"""
    current_user = request.current_user
    
    if current_user.role not in ['super_admin', 'admin', 'manager']:
        return jsonify({'code': 403, 'message': '无权限执行离职操作'}), 403
    
    target_user = UserV2.query.get_or_404(user_id)
    
    # 不能对自己操作
    if target_user.id == current_user.id:
        return jsonify({'code': 400, 'message': '不能对自己执行离职操作'}), 400
    
    # 店长只能处理本店员工
    if current_user.role == 'manager' and target_user.store_id != current_user.store_id:
        return jsonify({'code': 403, 'message': '只能处理本店员工'}), 403
    
    data = request.get_json()
    reason = data.get('reason', 'resignation')  # resignation/dismissal
    notes = data.get('notes', '')
    
    # 1. 标记用户为离职状态
    target_user.status = 'resigned'
    target_user.resigned_at = datetime.now()
    target_user.resigned_reason = notes
    target_user.resigned_by = current_user.id
    
    # 2. 清除第三方登录绑定
    target_user.wx_openid = None
    target_user.qq_openid = None
    
    db.session.commit()
    
    # 3. 归集数字资产（客户资源等）
    # TODO: 调用CRM/线索系统API获取该员工的客户/线索
    # 这里模拟数据
    transferred_assets = []
    
    # 示例：归集客户资源到公海
    # from app.models.crm_v2 import Customer
    # customers = Customer.query.filter_by(owner_id=target_user.employee_id).all()
    # for customer in customers:
    #     # 转移到公海
    #     customer.owner_id = None
    #     customer.is_in_public_sea = True
    #     # 记录转移
    #     transfer = DigitalAssetTransfer(
    #         from_user_id=target_user.id,
    #         from_employee_id=target_user.employee_id,
    #         to_user_id=None,  # 公海
    #         to_employee_id=None,
    #         asset_type='customer',
    #         asset_id=customer.id,
    #         asset_name=customer.name,
    #         transfer_reason=reason,
    #         transferred_by=current_user.id,
    #         notes=notes
    #     )
    #     db.session.add(transfer)
    #     transferred_assets.append({'type': 'customer', 'id': customer.id, 'name': customer.name})
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': {
            'user_id': target_user.id,
            'username': target_user.username,
            'resigned_at': target_user.resigned_at.strftime('%Y-%m-%d %H:%M:%S'),
            'transferred_assets_count': len(transferred_assets),
            'transferred_assets': transferred_assets
        },
        'message': f'员工{target_user.nickname}已离职，账户已回收，数字资产已归集到公海'
    })


@auth_v2_bp.route('/assets/transfer', methods=['POST'])
@jwt_required_v2
def transfer_assets(current_user):
    """分配数字资产（从公海分配给新人）"""
    current_user = request.current_user
    
    if current_user.role not in ['super_admin', 'admin', 'manager']:
        return jsonify({'code': 403, 'message': '无权限分配资产'}), 403
    
    data = request.get_json()
    asset_type = data.get('asset_type')  # customer/lead/contract/scheme
    asset_id = data.get('asset_id')
    to_user_id = data.get('to_user_id')
    
    if not all([asset_type, asset_id, to_user_id]):
        return jsonify({'code': 400, 'message': '缺少必要参数'}), 400
    
    to_user = UserV2.query.get_or_404(to_user_id)
    if to_user.status != 'active':
        return jsonify({'code': 400, 'message': '接收人账号状态异常'}), 400
    
    # TODO: 调用相应系统API转移资产所有权
    # 这里记录转移日志
    transfer = DigitalAssetTransfer(
        from_user_id=None,  # 从公海
        from_employee_id=None,
        to_user_id=to_user_id,
        to_employee_id=to_user.employee_id,
        asset_type=asset_type,
        asset_id=asset_id,
        asset_name=data.get('asset_name'),
        transfer_reason='manager_assign',
        transferred_by=current_user.id,
        notes=data.get('notes', '')
    )
    db.session.add(transfer)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': transfer.to_dict() if hasattr(transfer, 'to_dict') else {'id': transfer.id},
        'message': f'资产已分配给{to_user.nickname}'
    })


# ========== 用户管理 ==========

@auth_v2_bp.route('/users', methods=['GET'])
@jwt_required_v2
def get_users(current_user):
    """获取用户列表"""
    current_user = request.current_user
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', 'active')
    store_id = request.args.get('store_id', type=int)
    
    query = UserV2.query
    
    # 店长只能看本店
    if current_user.role == 'manager':
        query = query.filter_by(store_id=current_user.store_id)
    elif store_id:
        query = query.filter_by(store_id=store_id)
    
    if keyword:
        query = query.filter(
            db.or_(
                UserV2.username.contains(keyword),
                UserV2.nickname.contains(keyword),
                UserV2.phone.contains(keyword)
            )
        )
    
    if status:
        query = query.filter_by(status=status)
    
    total = query.count()
    users = query.order_by(UserV2.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return jsonify({
        'code': 200,
        'data': {
            'items': [u.to_dict(include_sensitive=current_user.role in ['super_admin', 'admin']) for u in users],
            'total': total,
            'page': page,
            'pageSize': page_size
        },
        'message': 'success'
    })


@auth_v2_bp.route('/users/<int:id>/unlock', methods=['POST'])
@jwt_required_v2
def unlock_user(current_user, id):
    """解锁被锁定的账号"""
    current_user = request.current_user
    
    if current_user.role not in ['super_admin', 'admin', 'manager']:
        return jsonify({'code': 403, 'message': '无权限解锁账号'}), 403
    
    user = UserV2.query.get_or_404(id)
    
    if current_user.role == 'manager' and user.store_id != current_user.store_id:
        return jsonify({'code': 403, 'message': '只能解锁本店员工'}), 403
    
    user.login_fail_count = 0
    user.locked_until = None
    db.session.commit()
    
    return jsonify({'code': 200, 'message': f'账号{user.username}已解锁'})


# ========== 门店管理 ==========

@auth_v2_bp.route('/stores', methods=['GET'])
@jwt_required_v2
def get_stores(current_user):
    """获取门店列表"""
    stores = Store.query.filter_by(status='active').all()
    return jsonify({
        'code': 200,
        'data': [s.to_dict() for s in stores],
        'message': 'success'
    })


@auth_v2_bp.route('/stores', methods=['POST'])
@jwt_required_v2
def create_store(current_user):
    """创建门店（需超管）"""
    current_user = request.current_user
    if current_user.role != 'super_admin':
        return jsonify({'code': 403, 'message': '只有超级管理员可以创建门店'}), 403
    
    data = request.get_json()
    store = Store(
        code=data['code'],
        name=data['name'],
        address=data.get('address'),
        phone=data.get('phone'),
        manager_id=data.get('manager_id')
    )
    db.session.add(store)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'data': store.to_dict(),
        'message': '门店创建成功'
    })


# ========== 当前用户信息 ==========

@auth_v2_bp.route('/me', methods=['GET'])
@jwt_required_v2
def get_current_user(current_user):
    """获取当前登录用户信息"""
    user = request.current_user
    return jsonify({
        'code': 200,
        'data': user,
        'message': 'success'
    })


@auth_v2_bp.route('/me/bindings', methods=['GET'])
@jwt_required_v2
def get_my_bindings(current_user):
    """获取当前用户的第三方绑定状态"""
    user = request.current_user
    return jsonify({
        'code': 200,
        'data': {
            'wechat': {
                'bound': user.wx_openid is not None,
                'nickname': user.wx_nickname,
                'avatar': user.wx_avatar,
                'bound_at': user.wx_bound_at.strftime('%Y-%m-%d %H:%M:%S') if user.wx_bound_at else None
            },
            'qq': {
                'bound': user.qq_openid is not None,
                'nickname': user.qq_nickname,
                'avatar': user.qq_avatar,
                'bound_at': user.qq_bound_at.strftime('%Y-%m-%d %H:%M:%S') if user.qq_bound_at else None
            }
        },
        'message': 'success'
    })
