"""
客户方案路由 - 处理客户自主选品提交的方案
与后台报价逻辑保持一致
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.scheme import CustomerScheme, SchemeItem
from app.models.material_sku import MaterialSKU
from app.models.quote import QUOTE_CATEGORIES
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime, date

scheme_bp = Blueprint('scheme', __name__, url_prefix='/api/v3/schemes')


def generate_scheme_no():
    """生成方案编号 SC + 年月日 + 4位序号（与Quote.quote_no格式一致）"""
    today = date.today().strftime('%Y%m%d')
    count = CustomerScheme.query.filter(
        CustomerScheme.scheme_no.like(f'SC{today}%')
    ).count()
    return f"SC{today}{count+1:04d}"


def calculate_category_summary(items_data):
    """
    计算分类汇总 - 与后台报价逻辑一致
    根据category_level1映射到报价分类
    """
    # 分类映射关系（与MaterialSKU.category和Quote.category_summary对应）
    category_mapping = {
        '硬装主材': 'hard_material',
        '施工服务': 'construction',
        '安装服务': 'installation',
        '配送服务': 'delivery',
        '搬运服务': 'moving',
        '设计服务': 'design',
        '全屋定制': 'custom',
        '成品家具': 'furniture',
        '软装饰品': 'soft',
        '电气设备': 'equipment',
        '基装': 'construction',
        '主材': 'hard_material',
        '固装家具': 'custom',
        '活动家具': 'furniture',
    }

    # 初始化分类汇总
    summary = {}
    for key, name in QUOTE_CATEGORIES:
        summary[key] = {
            'name': name,
            'amount': 0
        }

    # 汇总各分类金额
    for item in items_data:
        cat1 = item.get('category_level1', '')
        total_price = item.get('total_price', 0)

        # 映射到报价分类
        quote_cat = category_mapping.get(cat1, 'other')
        if quote_cat in summary:
            summary[quote_cat]['amount'] += total_price
        else:
            # 未匹配的分类归入other
            if 'other' not in summary:
                summary['other'] = {'name': '其他', 'amount': 0}
            summary['other']['amount'] += total_price

    return summary


def calculate_totals(items_data, management_fee_rate=0, tax_rate=0):
    """
    计算费用汇总 - 与后台报价逻辑一致
    """
    # 小计
    subtotal = sum(item.get('total_price', 0) for item in items_data)

    # 管理费
    management_fee = subtotal * (management_fee_rate / 100) if management_fee_rate else 0

    # 税费
    tax = subtotal * (tax_rate / 100) if tax_rate else 0

    # 总价
    total_amount = subtotal + management_fee + tax

    return {
        'subtotal': round(subtotal, 2),
        'management_fee': round(management_fee, 2),
        'management_fee_rate': management_fee_rate,
        'tax': round(tax, 2),
        'tax_rate': tax_rate,
        'total_amount': round(total_amount, 2)
    }


@scheme_bp.route('', methods=['POST'])
def create_scheme():
    """
    创建客户方案 - 与后台create_quote逻辑对齐
    """
    data = request.get_json()

    # 生成方案编号
    scheme_no = generate_scheme_no()

    # 处理方案明细 - 与QuoteItem格式对齐
    items_data = data.get('items', [])
    processed_items = []

    for idx, item_data in enumerate(items_data):
        sku_id = item_data.get('sku_id')
        sku = MaterialSKU.query.get(sku_id) if sku_id else None

        quantity = item_data.get('quantity', 1)
        unit_price = item_data.get('unit_price', 0)
        total_price = quantity * unit_price

        processed_item = {
            'room_name': item_data.get('room_name', '默认空间'),
            'category_level1': item_data.get('category_level1') or (sku.category_level1 if sku else ''),
            'category_level2': item_data.get('category_level2') or (sku.category_level2 if sku else ''),
            'category_level3': item_data.get('category_level3') or (sku.category_level3 if sku else ''),
            'sku_id': sku_id,
            'name': item_data.get('name') or (sku.name if sku else ''),
            'sku_code': item_data.get('sku_code') or (sku.sku_code if sku else ''),
            'spec': item_data.get('spec') or (sku.specification if sku else ''),
            'brand': item_data.get('brand') or (sku.brand if sku else ''),
            'unit': item_data.get('unit') or (sku.unit if sku else '件'),
            'main_image': item_data.get('main_image') or (sku.main_image if sku else ''),
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': total_price,
            'remark': item_data.get('remark', ''),
            'sort_order': idx
        }
        processed_items.append(processed_item)

    # 计算分类汇总 - 与报价一致
    category_summary = calculate_category_summary(processed_items)

    # 计算费用汇总 - 与报价一致
    totals = calculate_totals(
        processed_items,
        management_fee_rate=data.get('management_fee_rate', 0),
        tax_rate=data.get('tax_rate', 0)
    )

    # 统计信息
    total_quantity = sum(item['quantity'] for item in processed_items)
    room_names = set(item['room_name'] for item in processed_items if item['room_name'])
    room_count = len(room_names)

    # 创建方案主记录
    scheme = CustomerScheme(
        scheme_no=scheme_no,
        name=data.get('name', '未命名方案'),
        customer_id=data.get('customer_id'),
        customer_name=data.get('customer_name'),
        customer_phone=data.get('customer_phone'),
        style=data.get('style'),
        area=data.get('area'),
        stage=data.get('stage'),
        remark=data.get('remark'),
        category_summary=category_summary,
        subtotal=totals['subtotal'],
        management_fee=totals['management_fee'],
        management_fee_rate=totals['management_fee_rate'],
        tax=totals['tax'],
        tax_rate=totals['tax_rate'],
        total_amount=totals['total_amount'],
        total_quantity=total_quantity,
        room_count=room_count,
        status='submitted',  # 客户提交后直接进入submitted状态
        source='customer'
    )

    db.session.add(scheme)
    db.session.flush()  # 获取scheme.id

    # 创建方案明细 - 与QuoteItem一致
    for item_data in processed_items:
        scheme_item = SchemeItem(
            scheme_id=scheme.id,
            room_name=item_data['room_name'],
            category_level1=item_data['category_level1'],
            category_level2=item_data['category_level2'],
            category_level3=item_data['category_level3'],
            sku_id=item_data['sku_id'],
            name=item_data['name'],
            sku_code=item_data['sku_code'],
            spec=item_data['spec'],
            brand=item_data['brand'],
            unit=item_data['unit'],
            main_image=item_data['main_image'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            total_price=item_data['total_price'],
            remark=item_data['remark'],
            sort_order=item_data['sort_order']
        )
        db.session.add(scheme_item)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '方案提交成功',
        'data': {
            'scheme_no': scheme_no,
            'id': scheme.id,
            'total_amount': totals['total_amount'],
            'total_quantity': total_quantity
        }
    })


@scheme_bp.route('', methods=['GET'])
@jwt_required_v2
def list_schemes(current_user):
    """
    获取方案列表（后台管理用）- 与get_quotes格式对齐
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    status = request.args.get('status')
    keyword = request.args.get('keyword', '').strip()

    query = CustomerScheme.query

    if status:
        query = query.filter(CustomerScheme.status == status)

    if keyword:
        query = query.filter(
            db.or_(
                CustomerScheme.scheme_no.contains(keyword),
                CustomerScheme.name.contains(keyword),
                CustomerScheme.customer_name.contains(keyword)
            )
        )

    query = query.order_by(CustomerScheme.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    items = []
    for scheme in pagination.items:
        data = scheme.to_dict()
        # 添加统计信息
        data['category_summary'] = scheme.category_summary or {}
        items.append(data)

    return jsonify({
        'code': 200,
        'data': {
            'items': items,
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@scheme_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
def get_scheme(current_user, id):
    """
    获取方案详情 - 与get_quote格式对齐
    """
    scheme = CustomerScheme.query.get_or_404(id)

    data = scheme.to_dict(include_items=True)

    return jsonify({
        'code': 200,
        'data': data
    })


@scheme_bp.route('/<int:id>/status', methods=['PUT'])
@jwt_required_v2
def update_scheme_status(current_user, id):
    """
    更新方案状态 - 支持关联报价单
    """
    scheme = CustomerScheme.query.get_or_404(id)
    data = request.get_json()

    # 更新状态
    if 'status' in data:
        scheme.status = data['status']

    # 更新处理信息
    if 'handler_id' in data:
        scheme.handler_id = data['handler_id']
    if 'handler_name' in data:
        scheme.handler_name = data['handler_name']
    if 'handle_remark' in data:
        scheme.handle_remark = data['handle_remark']

    # 关联报价单
    if 'quote_id' in data:
        scheme.quote_id = data['quote_id']
    if 'quote_no' in data:
        scheme.quote_no = data['quote_no']

    # 记录处理时间
    scheme.handled_at = datetime.now()
    scheme.updated_at = datetime.now()

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '状态更新成功',
        'data': scheme.to_dict()
    })


@scheme_bp.route('/<int:id>/convert-to-quote', methods=['POST'])
@jwt_required_v2
def convert_to_quote(current_user, id):
    """
    将客户方案转换为报价单 - 一键生成报价
    """
    from app.models.quote import Quote, QuoteItem

    scheme = CustomerScheme.query.get_or_404(id)

    # 生成报价编号
    today = date.today().strftime('%Y%m%d')
    count = Quote.query.filter(Quote.quote_no.like(f'BJ{today}%')).count()
    quote_no = f"BJ{today}{count+1:04d}"

    # 创建报价单
    quote = Quote(
        tenant_id=current_user.get('tenant_id', '0'),
        quote_no=quote_no,
        customer_id=scheme.customer_id,
        cover_config={
            'template': 'modern',
            'primary_color': '#8B4513',
            'show_customer_info': True
        },
        service_team=[],
        category_summary=scheme.category_summary,
        subtotal=scheme.subtotal,
        management_fee=scheme.management_fee,
        management_fee_rate=scheme.management_fee_rate,
        tax=scheme.tax,
        tax_rate=scheme.tax_rate,
        total_amount=scheme.total_amount,
        valid_days=30,
        expire_date=date.today() + __import__('datetime').timedelta(days=30),
        status='draft',
        creator_id=current_user.get('id'),
        creator_name=current_user.get('name'),
        remark=f'由客户方案 {scheme.scheme_no} 转换生成'
    )

    db.session.add(quote)
    db.session.flush()

    # 复制方案明细到报价明细
    scheme_items = SchemeItem.query.filter_by(scheme_id=scheme.id).order_by(SchemeItem.sort_order).all()

    for item in scheme_items:
        quote_item = QuoteItem(
            quote_id=quote.id,
            room_name=item.room_name,
            category_level1=item.category_level1,
            category_level2=item.category_level2,
            category_level3=item.category_level3,
            item_type='product',
            sku_id=item.sku_id,
            name=item.name,
            spec=item.spec,
            brand=item.brand,
            unit=item.unit,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price,
            image=item.main_image,
            remark=item.remark,
            sort_order=item.sort_order
        )
        db.session.add(quote_item)

    # 更新方案状态
    scheme.status = 'quoted'
    scheme.quote_id = quote.id
    scheme.quote_no = quote_no
    scheme.handler_id = current_user.get('id')
    scheme.handler_name = current_user.get('name')
    scheme.handled_at = datetime.now()

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '转换成功',
        'data': {
            'quote_id': quote.id,
            'quote_no': quote_no,
            'scheme_id': scheme.id
        }
    })


@scheme_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_scheme(current_user, id):
    """删除方案"""
    scheme = CustomerScheme.query.get_or_404(id)

    # 先删除明细
    SchemeItem.query.filter_by(scheme_id=id).delete()

    # 删除主记录
    db.session.delete(scheme)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '删除成功'
    })
