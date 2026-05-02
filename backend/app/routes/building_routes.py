"""
楼盘管理模块 - API路由
V3.0 全新设计
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.building import (
    Building, BuildingFollow, BuildingCustomer,
    COOPERATION_STATUS, COOPERATION_TYPES, PROPERTY_TYPES, FOLLOW_TYPES, FOLLOW_RESULTS
)
from app.models.customer import Customer
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime, date

building_bp = Blueprint('building', __name__, url_prefix='/api/v3/buildings')


# ========== 楼盘管理 ==========

@building_bp.route('', methods=['GET'])
@jwt_required_v2
def get_buildings(current_user):
    """获取楼盘列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    city = request.args.get('city', '').strip()
    cooperation_status = request.args.get('cooperation_status')
    property_type = request.args.get('property_type')

    query = Building.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_enabled=True
    )

    if keyword:
        query = query.filter(
            db.or_(
                Building.name.contains(keyword),
                Building.alias.contains(keyword),
                Building.address.contains(keyword)
            )
        )

    if city:
        query = query.filter(Building.city.contains(city))
    if cooperation_status:
        query = query.filter_by(cooperation_status=cooperation_status)
    if property_type:
        query = query.filter_by(property_type=property_type)

    query = query.order_by(Building.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [b.to_dict() for b in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@building_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
def get_building(current_user, id):
    """获取楼盘详情"""
    building = Building.query.get_or_404(id)

    # 加载跟进记录
    follows = BuildingFollow.query.filter_by(
        building_id=id
    ).order_by(BuildingFollow.created_at.desc()).all()

    # 加载业主信息
    customers = db.session.query(
        BuildingCustomer, Customer
    ).join(
        Customer, BuildingCustomer.customer_id == Customer.id
    ).filter(
        BuildingCustomer.building_id == id
    ).all()

    data = building.to_dict()
    data['follows'] = [f.to_dict() for f in follows]
    data['customers'] = [
        {
            **bc.to_dict(),
            'customer_name': c.name,
            'customer_phone': c.phone
        }
        for bc, c in customers
    ]

    return jsonify({
        'code': 200,
        'data': data
    })


@building_bp.route('', methods=['POST'])
@jwt_required_v2
def create_building(current_user):
    """创建楼盘"""
    data = request.get_json()

    building = Building(
        tenant_id=current_user.get('tenant_id', '0'),
        name=data['name'],
        alias=data.get('alias'),
        province=data.get('province'),
        city=data.get('city'),
        district=data.get('district'),
        address=data.get('address'),
        longitude=data.get('longitude'),
        latitude=data.get('latitude'),
        developer=data.get('developer'),
        property_company=data.get('property_company'),
        build_year=data.get('build_year'),
        total_houses=data.get('total_houses'),
        property_type=data.get('property_type'),
        cooperation_status=data.get('cooperation_status', 'none'),
        cooperation_type=data.get('cooperation_type'),
        contact_name=data.get('contact_name'),
        contact_phone=data.get('contact_phone'),
        contact_position=data.get('contact_position'),
        cooperation_start_date=data.get('cooperation_start_date'),
        cooperation_end_date=data.get('cooperation_end_date'),
        cooperation_terms=data.get('cooperation_terms'),
        remark=data.get('remark')
    )

    db.session.add(building)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': building.to_dict()
    })


@building_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_building(current_user, id):
    """更新楼盘"""
    building = Building.query.get_or_404(id)
    data = request.get_json()

    fields = [
        'name', 'alias', 'province', 'city', 'district', 'address',
        'longitude', 'latitude', 'developer', 'property_company',
        'build_year', 'total_houses', 'property_type',
        'cooperation_status', 'cooperation_type',
        'contact_name', 'contact_phone', 'contact_position',
        'cooperation_start_date', 'cooperation_end_date',
        'cooperation_terms', 'remark', 'is_enabled'
    ]

    for field in fields:
        if field in data:
            setattr(building, field, data[field])

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': building.to_dict()
    })


@building_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_building(current_user, id):
    """删除楼盘"""
    building = Building.query.get_or_404(id)
    building.is_enabled = False
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


# ========== 跟进记录 ==========

@building_bp.route('/<int:building_id>/follows', methods=['GET'])
@jwt_required_v2
def get_follows(current_user, building_id):
    """获取楼盘跟进记录"""
    follows = BuildingFollow.query.filter_by(
        building_id=building_id
    ).order_by(BuildingFollow.created_at.desc()).all()

    return jsonify({
        'code': 200,
        'data': [f.to_dict() for f in follows]
    })


@building_bp.route('/<int:building_id>/follows', methods=['POST'])
@jwt_required_v2
def add_follow(current_user, building_id):
    """添加跟进记录"""
    data = request.get_json()

    follow = BuildingFollow(
        building_id=building_id,
        follow_type=data.get('follow_type'),
        content=data.get('content'),
        contact_name=data.get('contact_name'),
        contact_phone=data.get('contact_phone'),
        result=data.get('result'),
        next_follow_at=data.get('next_follow_at'),
        next_follow_content=data.get('next_follow_content'),
        operator_id=current_user.get('id'),
        operator_name=current_user.get('name'),
        attachments=data.get('attachments', [])
    )

    db.session.add(follow)

    # 更新楼盘合作状态
    if data.get('result') == 'cooperated':
        building = Building.query.get(building_id)
        if building:
            building.cooperation_status = 'cooperating'
            building.cooperation_start_date = date.today()

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': follow.to_dict()
    })


# ========== 业主管理 ==========

@building_bp.route('/<int:building_id>/customers', methods=['GET'])
@jwt_required_v2
def get_building_customers(current_user, building_id):
    """获取楼盘业主列表"""
    records = db.session.query(
        BuildingCustomer, Customer
    ).join(
        Customer, BuildingCustomer.customer_id == Customer.id
    ).filter(
        BuildingCustomer.building_id == building_id
    ).all()

    return jsonify({
        'code': 200,
        'data': [
            {
                **bc.to_dict(),
                'customer_name': c.name,
                'customer_phone': c.phone
            }
            for bc, c in records
        ]
    })


@building_bp.route('/<int:building_id>/customers', methods=['POST'])
@jwt_required_v2
def add_building_customer(current_user, building_id):
    """添加业主"""
    data = request.get_json()

    # 检查是否已存在
    existing = BuildingCustomer.query.filter_by(
        building_id=building_id,
        customer_id=data['customer_id']
    ).first()

    if existing:
        return jsonify({'code': 400, 'message': '该客户已是该楼盘业主'}), 400

    record = BuildingCustomer(
        building_id=building_id,
        customer_id=data['customer_id'],
        building_no=data.get('building_no'),
        unit_no=data.get('unit_no'),
        room_no=data.get('room_no'),
        floor=data.get('floor'),
        house_type=data.get('house_type'),
        house_area=data.get('house_area'),
        decoration_status=data.get('decoration_status', 'not_started'),
        owner_type=data.get('owner_type', 'owner'),
        remark=data.get('remark')
    )

    db.session.add(record)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': record.to_dict()
    })


# ========== 统计报表 ==========

@building_bp.route('/statistics', methods=['GET'])
@jwt_required_v2
def get_statistics(current_user):
    """获取楼盘统计"""
    tenant_id = current_user.get('tenant_id', '0')

    # 总数
    total = Building.query.filter_by(
        tenant_id=tenant_id,
        is_enabled=True
    ).count()

    # 合作状态统计
    status_stats = db.session.query(
        Building.cooperation_status,
        db.func.count(Building.id)
    ).filter_by(
        tenant_id=tenant_id,
        is_enabled=True
    ).group_by(Building.cooperation_status).all()

    # 本月新增
    current_month = date.today().replace(day=1)
    new_this_month = Building.query.filter(
        Building.tenant_id == tenant_id,
        Building.is_enabled == True,
        Building.created_at >= current_month
    ).count()

    # 合作中数量
    cooperating = Building.query.filter_by(
        tenant_id=tenant_id,
        is_enabled=True,
        cooperation_status='cooperating'
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'total': total,
            'by_status': {s: c for s, c in status_stats},
            'new_this_month': new_this_month,
            'cooperating': cooperating
        }
    })


# ========== 选项数据 ==========

@building_bp.route('/options', methods=['GET'])
@jwt_required_v2
def get_options(current_user):
    """获取楼盘相关选项"""
    return jsonify({
        'code': 200,
        'data': {
            'cooperation_status': [{'value': v, 'label': l} for v, l in COOPERATION_STATUS],
            'cooperation_types': [{'value': v, 'label': l} for v, l in COOPERATION_TYPES],
            'property_types': [{'value': v, 'label': l} for v, l in PROPERTY_TYPES],
            'follow_types': [{'value': v, 'label': l} for v, l in FOLLOW_TYPES],
            'follow_results': [{'value': v, 'label': l} for v, l in FOLLOW_RESULTS],
        }
    })
