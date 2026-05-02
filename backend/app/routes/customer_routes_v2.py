"""
客户系统 V2.0 API路由
支持：匿名选品、注册转化、线索沉淀
"""
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.customer import Customer, CustomerFollow
from app.models.lead_v2 import Lead, LeadFollow, LeadChannelStat
from app.models.auth_v2 import UserV2
from datetime import datetime
import jwt
import hashlib
import re

# 线索渠道常量
CHANNEL_WEBSITE = 'DESIGNARY网站自然流量'

# 创建蓝图 - 注意：这里不使用url_prefix，在__init__.py中注册
customer_v2_bp = Blueprint('customer_v2', __name__)


def generate_token(customer_id, phone):
    """生成JWT令牌"""
    from datetime import timedelta
    payload = {
        'customer_id': customer_id,
        'phone': phone,
        'type': 'customer',
        'exp': datetime.utcnow() + timedelta(days=30),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


@customer_v2_bp.route('/customer/register', methods=['POST'])
def customer_register():
    """
    客户注册
    - 创建客户账号
    - 沉淀为线索（DESIGNARY网站自然流量渠道）
    - 迁移匿名选品
    """
    data = request.get_json()
    
    nickname = data.get('nickname', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    source = data.get('source', 'website')
    channel = data.get('channel', CHANNEL_WEBSITE)
    anonymous_items = data.get('anonymous_items', [])
    
    # 验证必填
    if not nickname or not phone or not password:
        return jsonify({'code': 400, 'message': '昵称、手机号和密码必填'}), 400
    
    # 验证手机号
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return jsonify({'code': 400, 'message': '手机号格式错误'}), 400
    
    # 验证密码长度
    if len(password) < 6:
        return jsonify({'code': 400, 'message': '密码至少6位'}), 400
    
    # 检查手机号是否已注册
    existing_customer = Customer.query.filter_by(phone=phone).first()
    if existing_customer:
        return jsonify({'code': 409, 'message': '该手机号已注册，请直接登录'}), 409
    
    try:
        # 1. 创建客户
        customer = Customer(
            name=nickname,
            phone=phone,
            password_hash=hash_password(password),
            source=source,
            status='active',
            created_at=datetime.now(),
            last_contact_at=datetime.now()
        )
        db.session.add(customer)
        db.session.flush()  # 获取customer.id
        
        # 2. 沉淀为线索（待转化状态）
        lead = Lead(
            name=nickname,
            phone=phone,
            source=source,
            channel=channel,
            status='new',  # 新线索，待分配
            customer_id=customer.id,
            created_at=datetime.now(),
            # 选品意向信息
            selection_count=len(anonymous_items),
            selection_amount=sum(item.get('price', 0) * item.get('quantity', 1) for item in anonymous_items),
            notes=f'客户通过网站自主选品注册，选品{len(anonymous_items)}件，意向金额{sum(item.get("price", 0) * item.get("quantity", 1) for item in anonymous_items)}元'
        )
        db.session.add(lead)
        
        # 3. 更新渠道统计
        today = datetime.now().date()
        channel_stat = LeadChannelStat.query.filter_by(
            channel=channel,
            stat_date=today
        ).first()
        
        if channel_stat:
            channel_stat.total_count += 1
            channel_stat.website_register_count += 1
        else:
            channel_stat = LeadChannelStat(
                channel=channel,
                stat_date=today,
                total_count=1,
                website_register_count=1
            )
            db.session.add(channel_stat)
        
        # 4. 如果有匿名选品，创建客户方案草稿
        if anonymous_items:
            from app.models.scheme import CustomerScheme, SchemeItem
            
            scheme = CustomerScheme(
                customer_id=customer.id,
                name=f'{nickname}的选品方案',
                status='draft',
                total_amount=sum(item.get('price', 0) * item.get('quantity', 1) for item in anonymous_items),
                created_at=datetime.now()
            )
            db.session.add(scheme)
            db.session.flush()
            
            # 添加方案项目
            for idx, item in enumerate(anonymous_items):
                scheme_item = SchemeItem(
                    scheme_id=scheme.id,
                    item_type=item.get('type', 'product'),
                    item_id=item.get('id'),
                    item_name=item.get('name'),
                    space_name=item.get('space_name', '未分类'),
                    quantity=item.get('quantity', 1),
                    unit_price=item.get('price', 0),
                    total_price=item.get('price', 0) * item.get('quantity', 1),
                    image_url=item.get('image'),
                    sort_order=idx
                )
                db.session.add(scheme_item)
        
        db.session.commit()
        
        # 生成token
        token = generate_token(customer.id, phone)
        
        return jsonify({
            'code': 200,
            'data': {
                'token': token,
                'user': {
                    'id': customer.id,
                    'nickname': nickname,
                    'phone': phone,
                    'selection_count': len(anonymous_items)
                }
            },
            'message': '注册成功'
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        current_app.logger.error(f'客户注册失败: {str(e)}\n{traceback.format_exc()}')
        return jsonify({'code': 500, 'message': f'注册失败：{str(e)}'}), 500


@customer_v2_bp.route('/customer/login', methods=['POST'])
def customer_login():
    """客户登录"""
    data = request.get_json()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    
    if not phone or not password:
        return jsonify({'code': 400, 'message': '请输入手机号和密码'}), 400
    
    customer = Customer.query.filter_by(phone=phone).first()
    
    if not customer:
        return jsonify({'code': 401, 'message': '手机号或密码错误'}), 401
    
    if customer.password_hash != hash_password(password):
        return jsonify({'code': 401, 'message': '手机号或密码错误'}), 401
    
    # 更新最后联系时间
    customer.last_contact_at = datetime.now()
    db.session.commit()
    
    token = generate_token(customer.id, phone)
    
    return jsonify({
        'code': 200,
        'data': {
            'token': token,
            'user': {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone
            }
        },
        'message': '登录成功'
    })


@customer_v2_bp.route('/customer/profile', methods=['GET'])
def customer_profile():
    """获取客户资料"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'code': 401, 'message': '请先登录'}), 401
    
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        customer_id = payload.get('customer_id')
    except:
        return jsonify({'code': 401, 'message': '登录已过期'}), 401
    
    customer = Customer.query.get_or_404(customer_id)
    
    return jsonify({
        'code': 200,
        'data': {
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'address': customer.address,
            'created_at': customer.created_at.strftime('%Y-%m-%d %H:%M:%S') if customer.created_at else None
        }
    })


@customer_v2_bp.route('/selection/migrate', methods=['POST'])
def migrate_selection():
    """迁移匿名选品到登录用户"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'code': 401, 'message': '请先登录'}), 401
    
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        customer_id = payload.get('customer_id')
    except:
        return jsonify({'code': 401, 'message': '登录已过期'}), 401
    
    data = request.get_json()
    items = data.get('items', [])
    
    if not items:
        return jsonify({'code': 200, 'data': {'migrated': False, 'count': 0}})
    
    try:
        from app.models.scheme import CustomerScheme, SchemeItem
        
        # 查找或创建草稿方案
        scheme = CustomerScheme.query.filter_by(
            customer_id=customer_id,
            status='draft'
        ).first()
        
        if not scheme:
            customer = Customer.query.get(customer_id)
            scheme = CustomerScheme(
                customer_id=customer_id,
                name=f'{customer.name}的选品方案',
                status='draft',
                total_amount=0,
                created_at=datetime.now()
            )
            db.session.add(scheme)
            db.session.flush()
        
        # 添加选品项目
        migrated_count = 0
        for item in items:
            # 检查是否已存在
            existing = SchemeItem.query.filter_by(
                scheme_id=scheme.id,
                item_id=item.get('id'),
                item_type=item.get('type', 'product')
            ).first()
            
            if not existing:
                scheme_item = SchemeItem(
                    scheme_id=scheme.id,
                    item_type=item.get('type', 'product'),
                    item_id=item.get('id'),
                    item_name=item.get('name'),
                    space_name=item.get('space_name', '未分类'),
                    quantity=item.get('quantity', 1),
                    unit_price=item.get('price', 0),
                    total_price=item.get('price', 0) * item.get('quantity', 1),
                    image_url=item.get('image'),
                    sort_order=migrated_count
                )
                db.session.add(scheme_item)
                migrated_count += 1
        
        # 更新方案总价
        scheme.total_amount = sum(
            item.total_price for item in scheme.items
        )
        scheme.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': {
                'migrated': True,
                'count': migrated_count,
                'scheme_id': scheme.id
            },
            'message': f'成功迁移{migrated_count}件商品'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'迁移选品失败: {str(e)}')
        return jsonify({'code': 500, 'message': '迁移失败'}), 500


@customer_v2_bp.route('/selection/draft', methods=['POST'])
def save_draft():
    """保存选品草稿"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'code': 401, 'message': '请先登录'}), 401
    
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        customer_id = payload.get('customer_id')
    except:
        return jsonify({'code': 401, 'message': '登录已过期'}), 401
    
    data = request.get_json()
    items = data.get('items', [])
    
    try:
        from app.models.scheme import CustomerScheme, SchemeItem
        
        # 查找或创建草稿
        scheme = CustomerScheme.query.filter_by(
            customer_id=customer_id,
            status='draft'
        ).first()
        
        if scheme:
            # 清除旧项目
            SchemeItem.query.filter_by(scheme_id=scheme.id).delete()
        else:
            customer = Customer.query.get(customer_id)
            scheme = CustomerScheme(
                customer_id=customer_id,
                name=f'{customer.name}的选品方案',
                status='draft',
                created_at=datetime.now()
            )
            db.session.add(scheme)
            db.session.flush()
        
        # 添加新项目
        for idx, item in enumerate(items):
            scheme_item = SchemeItem(
                scheme_id=scheme.id,
                item_type=item.get('type', 'product'),
                item_id=item.get('id'),
                item_name=item.get('name'),
                space_name=item.get('space_name', '未分类'),
                quantity=item.get('quantity', 1),
                unit_price=item.get('price', 0),
                total_price=item.get('price', 0) * item.get('quantity', 1),
                image_url=item.get('image'),
                sort_order=idx
            )
            db.session.add(scheme_item)
        
        scheme.total_amount = sum(
            item.get('price', 0) * item.get('quantity', 1) for item in items
        )
        scheme.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'data': {'scheme_id': scheme.id},
            'message': '草稿已保存'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'保存草稿失败: {str(e)}')
        return jsonify({'code': 500, 'message': '保存失败'}), 500


@customer_v2_bp.route('/packages/recommend', methods=['GET'])
def recommend_packages():
    """
    推荐套餐（星巴克大杯原理）
    根据客户当前选品总价，推荐接近的套餐方案
    """
    total_price = request.args.get('total_price', 0, type=float)
    
    # 模拟推荐数据（实际应从数据库查询）
    all_packages = [
        {
            'id': 1,
            'name': '经济型套餐',
            'description': '基础配置，适合预算有限',
            'price': 80000,
            'image': '/package-1.jpg'
        },
        {
            'id': 2,
            'name': '舒适家套餐',
            'description': '两室一厅基础配置，适合小家庭',
            'price': 120000,
            'image': '/package-2.jpg'
        },
        {
            'id': 3,
            'name': '品质生活套餐',
            'description': '三室两厅升级配置，品质之选',
            'price': 164200,
            'image': '/package-3.jpg'
        },
        {
            'id': 4,
            'name': '尊享全案套餐',
            'description': '全屋定制高端配置，尊享服务',
            'price': 178500,
            'image': '/package-4.jpg'
        },
        {
            'id': 5,
            'name': '奢华定制套餐',
            'description': '顶级配置，专属定制',
            'price': 250000,
            'image': '/package-5.jpg'
        }
    ]
    
    # 按接近程度排序
    recommendations = []
    for pkg in all_packages:
        diff = pkg['price'] - total_price
        diff_percent = abs(diff / total_price * 100) if total_price > 0 else 100
        
        recommendations.append({
            **pkg,
            'diff': diff,
            'diff_percent': round(diff_percent, 1),
            'is_highlight': diff > 0 and diff < 50000  # 高出但不超过5万的推荐
        })
    
    # 按接近程度排序
    recommendations.sort(key=lambda x: abs(x['diff']))
    
    # 取前3个
    top_recommendations = recommendations[:3]
    
    return jsonify({
        'code': 200,
        'data': {
            'current_total': total_price,
            'recommendations': top_recommendations
        }
    })
