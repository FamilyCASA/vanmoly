"""
客户管理模块 - API路由
从 vanmoly-distilled 蒸馏而来
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.customer import Customer, CustomerFollow, CUSTOMER_SOURCES, CUSTOMER_TYPES, CUSTOMER_STATUS, PRIORITY_OPTIONS, FOLLOW_TYPES
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime

customer_bp = Blueprint('customer', __name__, url_prefix='/api/v3/customers')


@customer_bp.route('', methods=['GET'])
@jwt_required_v2
def get_customers(current_user):
    """获取客户列表"""
    # 查询参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    status = request.args.get('status', '').strip()
    customer_type = request.args.get('customer_type', '').strip()
    source = request.args.get('source', '').strip()
    owner_id = request.args.get('owner_id', type=int)
    priority = request.args.get('priority', '').strip()

    # 构建查询
    query = Customer.query.filter_by(is_deleted=False)

    if keyword:
        query = query.filter(
            db.or_(
                Customer.name.contains(keyword),
                Customer.phone.contains(keyword),
                Customer.building_name.contains(keyword)
            )
        )

    if status:
        query = query.filter_by(status=status)
    if customer_type:
        query = query.filter_by(customer_type=customer_type)
    if source:
        query = query.filter_by(source=source)
    if owner_id:
        query = query.filter_by(owner_id=owner_id)
    if priority:
        query = query.filter_by(priority=priority)

    # 排序和分页
    query = query.order_by(Customer.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [c.to_dict() for c in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@customer_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
def get_customer(current_user, id):
    """获取客户详情"""
    from app.models.service_workflow import CustomerWorkflow

    customer = Customer.query.get_or_404(id)
    data = customer.to_dict(include_follows=True)

    # 加载关联的流程
    workflows = CustomerWorkflow.query.filter_by(
        customer_id=id,
        is_deleted=False
    ).order_by(CustomerWorkflow.created_at.desc()).all()

    data['workflows'] = [w.to_dict() for w in workflows]

    return jsonify({
        'code': 200,
        'data': data
    })


@customer_bp.route('', methods=['POST'])
@jwt_required_v2
def create_customer(current_user):
    """创建客户"""
    data = request.get_json()

    # 必填字段验证
    if not data.get('name') or not data.get('phone'):
        return jsonify({'code': 400, 'message': '姓名和电话为必填项'}), 400

    # 检查手机号是否已存在
    existing = Customer.query.filter_by(phone=data['phone'], is_deleted=False).first()
    if existing:
        return jsonify({'code': 400, 'message': '该手机号已存在'}), 400

    # 创建客户
    customer = Customer(
        name=data['name'],
        phone=data['phone'],
        gender=data.get('gender', '未知'),
        email=data.get('email'),
        wechat=data.get('wechat'),
        address=data.get('address'),
        province=data.get('province'),
        city=data.get('city'),
        district=data.get('district'),
        street=data.get('street'),
        detail_address=data.get('detail_address'),
        building_name=data.get('building_name'),
        source=data.get('source'),
        budget=data.get('budget'),
        house_type=data.get('house_type'),
        house_area=data.get('house_area'),
        requirements=data.get('requirements'),
        style_preference=data.get('style_preference'),
        customer_type=data.get('customer_type', '已接触'),
        status=data.get('status', '待跟进'),
        priority=data.get('priority', '普通'),
        owner_id=data.get('owner_id'),
        remark=data.get('remark'),
        tenant_id=data.get('tenant_id', '0')
    )

    db.session.add(customer)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': customer.to_dict()
    })


@customer_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_customer(current_user, id):
    """更新客户"""
    customer = Customer.query.get_or_404(id)
    data = request.get_json()

    # 更新字段
    fields = [
        'name', 'phone', 'gender', 'email', 'wechat',
        'address', 'province', 'city', 'district', 'street',
        'detail_address', 'building_name',
        'source', 'budget', 'house_type', 'house_area',
        'requirements', 'style_preference',
        'customer_type', 'status', 'priority', 'owner_id', 'remark'
    ]

    for field in fields:
        if field in data:
            setattr(customer, field, data[field])

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': customer.to_dict()
    })


@customer_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_customer(current_user, id):
    """删除客户（软删除）"""
    customer = Customer.query.get_or_404(id)
    customer.is_deleted = True
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@customer_bp.route('/<int:id>/follow', methods=['POST'])
@jwt_required_v2
def add_follow(current_user, id):
    """添加跟进记录"""
    customer = Customer.query.get_or_404(id)
    data = request.get_json()

    # 创建跟进记录
    follow = CustomerFollow(
        customer_id=id,
        follow_type=data.get('follow_type', '其他'),
        content=data.get('content'),
        next_follow_at=datetime.fromisoformat(data['next_follow_at']) if data.get('next_follow_at') else None,
        operator_id=current_user.get('id')
    )

    db.session.add(follow)

    # 更新客户跟进统计
    customer.follow_count = (customer.follow_count or 0) + 1
    customer.last_follow = datetime.utcnow()
    if data.get('next_follow_at'):
        customer.next_follow = datetime.fromisoformat(data['next_follow_at'])

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '跟进记录添加成功',
        'data': follow.to_dict()
    })


@customer_bp.route('/stats', methods=['GET'])
@jwt_required_v2
def get_stats(current_user):
    """获取客户统计"""
    # 总客户数
    total = Customer.query.filter_by(is_deleted=False).count()

    # 按状态统计
    status_stats = db.session.query(
        Customer.status,
        db.func.count(Customer.id)
    ).filter(
        Customer.is_deleted == False,
        Customer.status != None
    ).group_by(Customer.status).all()

    # 按类型统计
    type_stats = db.session.query(
        Customer.customer_type,
        db.func.count(Customer.id)
    ).filter(
        Customer.is_deleted == False,
        Customer.customer_type != None
    ).group_by(Customer.customer_type).all()

    # 按来源统计
    source_stats = db.session.query(
        Customer.source,
        db.func.count(Customer.id)
    ).filter(
        Customer.is_deleted == False,
        Customer.source != None
    ).group_by(Customer.source).all()

    # 本月新增
    from datetime import datetime, timedelta
    first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    this_month = Customer.query.filter(
        Customer.is_deleted == False,
        Customer.created_at >= first_day
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'total': total,
            'this_month': this_month,
            'by_status': {s: c for s, c in status_stats},
            'by_type': {t: c for t, c in type_stats},
            'by_source': {s: c for s, c in source_stats}
        }
    })


@customer_bp.route('/sources', methods=['GET'])
@jwt_required_v2
def get_sources(current_user):
    """获取客户来源列表"""
    return jsonify({
        'code': 200,
        'data': CUSTOMER_SOURCES
    })


@customer_bp.route('/options', methods=['GET'])
@jwt_required_v2
def get_options(current_user):
    """获取客户相关选项"""
    return jsonify({
        'code': 200,
        'data': {
            'sources': CUSTOMER_SOURCES,
            'customer_types': CUSTOMER_TYPES,
            'status_list': CUSTOMER_STATUS,
            'priorities': PRIORITY_OPTIONS,
            'follow_types': FOLLOW_TYPES
        }
    })
@customer_bp.route('/search', methods=['GET'])
def search_customers():
    """搜索客户（支持名称关键词，返回id/name/phone）"""
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    query = Customer.query.filter_by(is_deleted=False)
    if keyword:
        query = query.filter(Customer.name.ilike(f'%{keyword}%'))
    
    pagination = query.order_by(Customer.created_at.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    return jsonify({
        'code': 200,
        'data': {
            'items': [{'id': c.id, 'name': c.name, 'phone': c.phone} for c in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        }
    })

