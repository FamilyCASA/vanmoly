"""
报价管理模块 - API路由
V3.0 全新设计
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.quote import Quote, QuoteItem, QuoteTemplate, QUOTE_CATEGORIES, SERVICE_ROLES, ROOM_OPTIONS, QUOTE_STATUS, MeasurementRule, DEFAULT_MEASUREMENT_RULES
from app.models.customer import Customer
from app.models import Employee  # 从 hr_v2 导入
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime, date, timedelta

quote_bp = Blueprint('quote', __name__, url_prefix='/api/v3/quotes')


# ========== 计量值计算（规则引擎）==========

# 单位分类映射
LENGTH_UNITS = ('米', 'm', '延米')
AREA_UNITS = ('平方米', '㎡', 'm²', 'm2', '平米')
VOLUME_UNITS = ('立方米', 'm³', 'm3')
QUANTITY_UNITS = ('件', '个', '套', '组', '项', '张', '块', '条', '根', '把', '对', '只', '支', '片', '台', '扇')


def _classify_unit(unit):
    """将单位归类为 length/area/volume/quantity"""
    u = (unit or '').lower().strip()
    if u in LENGTH_UNITS:
        return 'length'
    if u in AREA_UNITS:
        return 'area'
    if u in VOLUME_UNITS:
        return 'volume'
    return 'quantity'


def _get_measurement_rules(tenant_id='0'):
    """从数据库加载启用的计量规则，按优先级排序"""
    try:
        from app.models.quote import MeasurementRule
        rules = MeasurementRule.query.filter_by(
            tenant_id=tenant_id, is_enabled=True, is_deleted=False
        ).order_by(MeasurementRule.priority.asc(), MeasurementRule.sort_order.asc()).all()
        return [r for r in rules]
    except Exception:
        return []


def _apply_height_adjustment(height, params):
    """根据阈值调整高度值"""
    thresholds = params.get('thresholds', [])
    if not thresholds:
        return height
    # 阈值从小到大排序，找到第一个满足的
    sorted_thresh = sorted(thresholds, key=lambda x: x.get('min', 0))
    for t in sorted_thresh:
        if height < t['min']:
            height = t['adjust_to']
            break
    return height


def calc_measurement_value(unit, width=None, depth=None, height=None, manual_value=None,
                           category_level2=None, custom_name=None, material_name=None,
                           process_name=None, rules=None):
    """根据规则引擎计算计量值

    规则优先级：
    1. 手动值覆盖
    2. 特殊修正规则（门套/四方/投影/柜门/赠送等）
    3. 基础计算规则（长度/面积/体积/数量）
    """
    # 1. 手动值优先
    if manual_value is not None:
        try:
            if float(manual_value) > 0:
                return float(manual_value)
        except (ValueError, TypeError):
            pass

    # 解析尺寸（mm）
    w = float(width) if width else 0
    d = float(depth) if depth else 0
    h = float(height) if height else 0
    dims = [v for v in [w, d, h] if v > 0]
    if not dims:
        return 1

    # 辅助函数：检查关键词匹配
    def _match_keywords(text, keywords_str):
        if not text or not keywords_str:
            return False
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
        text_lower = str(text).lower()
        return any(kw.lower() in text_lower for kw in keywords)

    # 加载规则（如果未传入）
    if rules is None:
        rules = _get_measurement_rules()

    # 工艺赠送检测
    process_free = False
    for rule in rules:
        if rule.rule_type == 'process_free':
            if rule.match_field == 'process_name' and _match_keywords(process_name, rule.match_value):
                process_free = True
                break

    # 高度调整（投影规则）
    adjusted_h = h
    for rule in rules:
        if rule.rule_type == 'adjust_height':
            field_val = ''
            if rule.match_field == 'category_level2':
                field_val = category_level2 or ''
            elif rule.match_field == 'category_level1':
                field_val = ''
            if _match_keywords(field_val, rule.match_value):
                adjusted_h = _apply_height_adjustment(h, rule.rule_params or {})
                break

    # 重新构建尺寸数组（使用调整后的高度）
    adjusted_dims = [v for v in [w, d, adjusted_h] if v > 0]
    if not adjusted_dims:
        adjusted_dims = dims

    # 2. 检查特殊规则
    unit_cat = _classify_unit(unit)

    # 门套/垭口套
    for rule in rules:
        if rule.rule_type == 'door_frame':
            field_val = ''
            if rule.match_field == 'name':
                field_val = material_name or ''
            if _match_keywords(field_val, rule.match_value) and unit_cat == 'length':
                # (高度×2 + 宽度) / 1000
                return round((adjusted_h * 2 + w) / 1000.0, 4)

    # 四方轮廓
    for rule in rules:
        if rule.rule_type == 'four_sided':
            field_val = ''
            if rule.match_field == 'custom_name':
                field_val = custom_name or ''
            if _match_keywords(field_val, rule.match_value) and unit_cat == 'length':
                # (宽度 + 高度) × 2 / 1000
                return round((w + adjusted_h) * 2 / 1000.0, 4)

    # 3. 基础计算
    result = 1
    if unit_cat == 'length':
        result = max(adjusted_dims) / 1000.0
    elif unit_cat == 'area':
        if len(adjusted_dims) >= 2:
            sorted_dims = sorted(adjusted_dims, reverse=True)
            result = (sorted_dims[0] * sorted_dims[1]) / 1000000.0
        else:
            result = max(adjusted_dims) / 1000.0
    elif unit_cat == 'volume':
        result = (w * d * adjusted_h) / 1000000000.0
    else:
        result = 1

    result = round(result, 4)

    # 4. 柜门面积保底
    for rule in rules:
        if rule.rule_type == 'adjust_min_area':
            field_val = ''
            if rule.match_field == 'category_level2':
                field_val = category_level2 or ''
            if _match_keywords(field_val, rule.match_value) and result < rule.rule_params.get('min_value', 0):
                result = rule.rule_params['min_value']
            break

    return result


def calc_item_total_price(item, rules=None):
    """计算单项总价: qty * measurement_value * unit_price + craft_amount(受赠送规则影响)"""
    qty = float(item.quantity or 1)
    m_val = float(item.measurement_value or 1)
    u_price = float(item.unit_price or 0)

    # 工艺金额
    process_amount = float(item.process_amount or 0)
    if process_amount > 0:
        # 检查赠送规则
        if rules is None:
            rules = _get_measurement_rules()
        process_name = getattr(item, 'process_name', None) or ''
        for rule in rules:
            if rule.rule_type == 'process_free':
                keywords = rule.match_value or ''
                if keywords.strip().lower() in str(process_name).lower():
                    process_amount = 0
                    break

    return round(qty * m_val * u_price + process_amount, 2)


# ========== 报价模板 ==========

@quote_bp.route('/templates', methods=['GET'])
@jwt_required_v2
def get_templates(current_user):
    """获取报价封面模板"""
    templates = QuoteTemplate.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_enabled=True
    ).order_by(QuoteTemplate.sort_order).all()

    return jsonify({
        'code': 200,
        'data': [t.to_dict() for t in templates]
    })


@quote_bp.route('/templates', methods=['POST'])
@jwt_required_v2
def create_template(current_user):
    """创建模板"""
    data = request.get_json()

    template = QuoteTemplate(
        tenant_id=current_user.get('tenant_id', '0'),
        name=data['name'],
        template_type=data.get('template_type', 'modern'),
        style_config=data.get('style_config', {}),
        background_images=data.get('background_images', []),
        watermark_config=data.get('watermark_config', {}),
        is_default=data.get('is_default', False),
        sort_order=data.get('sort_order', 0)
    )

    db.session.add(template)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': template.to_dict()
    })


@quote_bp.route('/templates/<int:template_id>', methods=['PUT'])
@jwt_required_v2
def update_template(current_user, template_id):
    """更新模板"""
    template = QuoteTemplate.query.get_or_404(template_id)
    data = request.get_json()
    if data.get('name'):
        template.name = data['name']
    if 'template_type' in data:
        template.template_type = data['template_type']
    if 'style_config' in data:
        template.style_config = data['style_config']
    if 'background_images' in data:
        template.background_images = data['background_images']
    if 'watermark_config' in data:
        template.watermark_config = data['watermark_config']
    if 'is_default' in data:
        template.is_default = data['is_default']
    if 'sort_order' in data:
        template.sort_order = data['sort_order']
    if 'is_enabled' in data:
        template.is_enabled = data['is_enabled']
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': template.to_dict()
    })


@quote_bp.route('/templates/<int:template_id>', methods=['DELETE'])
@jwt_required_v2
def delete_template(current_user, template_id):
    """删除模板"""
    template = QuoteTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


# ========== 报价管理 ==========

@quote_bp.route('', methods=['GET'])
@jwt_required_v2
def get_quotes(current_user):
    """获取报价列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    customer_id = request.args.get('customer_id', type=int)
    status = request.args.get('status')

    query = Quote.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_deleted=False
    )

    if keyword:
        query = query.filter(
            db.or_(
                Quote.quote_no.contains(keyword),
            )
        )

    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if status:
        query = query.filter_by(status=status)

    query = query.order_by(Quote.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    items = []
    for quote in pagination.items:
        data = quote.to_dict()
        # customer_name/customer_phone already in to_dict from redundant fields
        # Fallback: try main DB if redundant fields are empty
        if not data.get('customer_name'):
            try:
                customer = Customer.query.get(quote.customer_id)
                data['customer_name'] = customer.name if customer else None
                data['customer_phone'] = customer.phone if customer else None
            except Exception:
                pass
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


@quote_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
def get_quote(current_user, id):
    """获取报价详情"""
    quote = Quote.query.get_or_404(id)

    data = quote.to_dict(include_items=True)

    # 客户信息
    customer = Customer.query.get(quote.customer_id)
    data['customer'] = customer.to_dict() if customer else None

    return jsonify({
        'code': 200,
        'data': data
    })


@quote_bp.route('', methods=['POST'])
@jwt_required_v2
def create_quote(current_user):
    """创建报价"""
    data = request.get_json()

    # 生成报价编号
    today = date.today().strftime('%Y%m%d')
    count = Quote.query.filter(
        Quote.quote_no.like(f'BJ{today}%')
    ).count()
    quote_no = f"BJ{today}{count+1:04d}"

    # 计算过期日期
    valid_days = data.get('valid_days', 30)
    expire_date = date.today() + timedelta(days=valid_days)

    # 获取客户信息并冗余存储（独立数据库不支持外键引用主库）
    customer = Customer.query.get(data.get('customer_id')) if data.get('customer_id') else None

    quote = Quote(
        tenant_id=current_user.get('tenant_id', '0'),
        quote_no=quote_no,
        customer_id=data.get('customer_id'),
        customer_name=customer.name if customer else '',
        customer_phone=customer.phone if customer else '',
        cover_config=data.get('cover_config', {}),
        project_name=data.get('project_name'),
        project_address=data.get('project_address'),
        house_type=data.get('house_type'),
        related_case_id=data.get('related_case_id'),
        contract_no=data.get('contract_no'),
        cover_template_id=data.get('cover_template_id'),
        service_team=data.get('service_team', []),
        category_summary=data.get('category_summary', {}),
        subtotal=data.get('subtotal', 0),
        management_fee=data.get('management_fee', 0),
        management_fee_rate=data.get('management_fee_rate', 0),
        tax=data.get('tax', 0),
        tax_rate=data.get('tax_rate', 0),
        total_amount=data.get('total_amount', 0),
        valid_days=valid_days,
        expire_date=expire_date,
        status='draft',
        creator_id=current_user.get('id'),
        creator_name=current_user.get('name'),
        remark=data.get('remark')
    )

    db.session.add(quote)
    db.session.flush()

    # 添加报价项
    for item_data in data.get('items', []):
        w = item_data.get('width')
        d = item_data.get('depth')
        h = item_data.get('height')
        unit = item_data.get('unit', '项')
        m_val = calc_measurement_value(
            unit, width=w, depth=d, height=h,
            manual_value=item_data.get('measurement_value'),
            category_level2=item_data.get('category_level2'),
            custom_name=item_data.get('custom_name'),
            material_name=item_data.get('name'),
            process_name=item_data.get('process_name')
        )
        item = QuoteItem(
            quote_id=quote.id,
            room_name=item_data.get('room_name'),
            category_level1=item_data.get('category_level1'),
            category_level2=item_data.get('category_level2'),
            category_level3=item_data.get('category_level3'),
            item_type=item_data.get('item_type', 'product'),
            sku_id=item_data.get('sku_id'),
            name=item_data.get('name'),
            spec=item_data.get('spec'),
            brand=item_data.get('brand'),
            unit=unit,
            quantity=item_data.get('quantity', 1),
            unit_price=item_data.get('unit_price', 0),
            width=w,
            depth=d,
            height=h,
            measurement_value=m_val,
            craft_type=item_data.get('craft_type'),
            craft_price=item_data.get('craft_price', 0),
            craft_quantity=item_data.get('craft_quantity', 1),
            craft_coefficient=item_data.get('craft_coefficient', 1),
            image=item_data.get('image'),
            remark=item_data.get('remark'),
            sort_order=item_data.get('sort_order', 0)
        )
        item.total_price = calc_item_total_price(item)
        db.session.add(item)

    db.session.commit()
    _recalculate_quote_total(quote.id)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': quote.to_dict(include_items=True)
    })


@quote_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_quote(current_user, id):
    """更新报价"""
    quote = Quote.query.get_or_404(id)
    data = request.get_json()

    # 只有草稿可以修改
    if quote.status != 'draft':
        return jsonify({'code': 400, 'message': '只有草稿状态可以修改'}), 400

    fields = [
        'cover_config', 'project_name', 'project_address', 'house_type',
        'related_case_id', 'contract_no', 'cover_template_id',
        'service_team', 'category_summary',
        'customer_name', 'customer_phone',
        'subtotal', 'management_fee', 'management_fee_rate',
        'tax', 'tax_rate', 'total_amount', 'valid_days', 'remark'
    ]

    for field in fields:
        if field in data:
            setattr(quote, field, data[field])

    # 更新过期日期
    if 'valid_days' in data:
        quote.expire_date = date.today() + timedelta(days=data['valid_days'])

    # 更新报价项
    if 'items' in data:
        # 删除旧项
        QuoteItem.query.filter_by(quote_id=id).delete()

        # 添加新项
        for item_data in data['items']:
            w = item_data.get('width')
            dp = item_data.get('depth')
            h = item_data.get('height')
            unit = item_data.get('unit', '项')
            m_val = calc_measurement_value(
                unit, width=w, depth=dp, height=h,
                manual_value=item_data.get('measurement_value'),
                category_level2=item_data.get('category_level2'),
                custom_name=item_data.get('custom_name'),
                material_name=item_data.get('name'),
                process_name=item_data.get('process_name')
            )
            item = QuoteItem(
                quote_id=id,
                room_name=item_data.get('room_name'),
                category_level1=item_data.get('category_level1'),
                category_level2=item_data.get('category_level2'),
                category_level3=item_data.get('category_level3'),
                item_type=item_data.get('item_type', 'product'),
                sku_id=item_data.get('sku_id'),
                name=item_data.get('name'),
                spec=item_data.get('spec'),
                brand=item_data.get('brand'),
                unit=unit,
                quantity=item_data.get('quantity', 1),
                unit_price=item_data.get('unit_price', 0),
                width=w,
                depth=dp,
                height=h,
                measurement_value=m_val,
                craft_type=item_data.get('craft_type'),
                craft_price=item_data.get('craft_price', 0),
                craft_quantity=item_data.get('craft_quantity', 1),
                craft_coefficient=item_data.get('craft_coefficient', 1),
                image=item_data.get('image'),
                remark=item_data.get('remark'),
                sort_order=item_data.get('sort_order', 0)
            )
            item.total_price = calc_item_total_price(item)
            db.session.add(item)

    db.session.commit()
    _recalculate_quote_total(id)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': quote.to_dict(include_items=True)
    })


@quote_bp.route('/<int:id>/send', methods=['POST'])
@jwt_required_v2
def send_quote(current_user, id):
    """发送报价"""
    quote = Quote.query.get_or_404(id)
    quote.status = 'sent'
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '已发送',
        'data': quote.to_dict()
    })


@quote_bp.route('/<int:id>/confirm', methods=['POST'])
@jwt_required_v2
def confirm_quote(current_user, id):
    """确认报价 - 自动生成双版本PDF并授权案例"""
    quote = Quote.query.get_or_404(id)

    if quote.status not in ('sent', 'draft'):
        return jsonify({'code': 400, 'message': '当前状态不可确认'}), 400

    quote.status = 'confirmed'
    db.session.commit()

    # Auto-generate PDFs (customer + visitor)
    pdf_result = None
    try:
        from app.utils.pdf_generator import generate_both_pdfs
        pdf_result = generate_both_pdfs(id, show_ref=True)
    except Exception as e:
        import traceback
        traceback.print_exc()

    # Auto-authorize related case
    auth_result = None
    try:
        from app.utils.pdf_generator import auto_authorize_on_quote_confirm
        auth_result = auto_authorize_on_quote_confirm(id)
    except Exception as e:
        import traceback
        traceback.print_exc()

    result = quote.to_dict(include_items=True)
    if pdf_result:
        result['pdf_customer'] = pdf_result.get('customer_path')
        result['pdf_visitor'] = pdf_result.get('visitor_path')
    if auth_result:
        result['authorization'] = auth_result

    return jsonify({
        'code': 200,
        'message': '报价已确认',
        'data': result
    })


@quote_bp.route('/<int:id>/sign', methods=['POST'])
@jwt_required_v2
def sign_quote(current_user, id):
    """签署报价"""
    quote = Quote.query.get_or_404(id)
    data = request.get_json()

    quote.signature_customer = data.get('signature_customer')
    quote.signature_planner = data.get('signature_planner')
    quote.signature_manager = data.get('signature_manager')
    quote.signature_seal = data.get('signature_seal')
    quote.signed_at = datetime.utcnow()
    quote.status = 'signed'

    db.session.commit()

    # Also generate PDFs and auto-authorize on signing
    pdf_result = None
    try:
        from app.utils.pdf_generator import generate_both_pdfs
        pdf_result = generate_both_pdfs(id)
    except Exception as e:
        import traceback
        traceback.print_exc()

    auth_result = None
    try:
        from app.utils.pdf_generator import auto_authorize_on_quote_confirm
        auth_result = auto_authorize_on_quote_confirm(id)
    except Exception as e:
        import traceback
        traceback.print_exc()

    result = quote.to_dict(include_items=True)
    if pdf_result:
        result['pdf_customer'] = pdf_result.get('customer_path')
        result['pdf_visitor'] = pdf_result.get('visitor_path')
    if auth_result:
        result['authorization'] = auth_result

    return jsonify({
        'code': 200,
        'message': '签署成功',
        'data': result
    })


@quote_bp.route('/<int:id>/pdf', methods=['GET'])
@jwt_required_v2
def download_pdf(current_user, id):
    """下载报价PDF（访客版）"""
    from flask import send_from_directory
    from pathlib import Path

    quote = Quote.query.get_or_404(id)

    # 查找最新的访客版 PDF
    upload_root = Path(__file__).parent.parent.parent / 'upload'
    pdf_dir = upload_root / 'pdf'

    pattern = f'quote_{quote.quote_no}_visitor_*.pdf'
    import glob as _glob
    files = sorted(_glob.glob(str(pdf_dir / pattern)), reverse=True)

    if not files:
        return jsonify({'code': 404, 'message': 'PDF文件不存在，请先生成'}), 404

    file_path = Path(files[0])
    # 安全检查
    if not str(file_path.resolve()).startswith(str(pdf_dir.resolve())):
        return jsonify({'code': 403, 'message': '非法文件路径'}), 403

    return send_from_directory(pdf_dir, file_path.name, as_attachment=True)


@quote_bp.route('/<int:id>/pdf-preview', methods=['GET'])
@jwt_required_v2
def pdf_preview(current_user, id):
    """生成报价PDF预览（支持紧凑/完整两种视图）
    Query param: show_ref=true(完整)/false(紧凑，默认true)
    """
    from flask import request, send_from_directory
    from pathlib import Path

    quote = Quote.query.get_or_404(id)
    show_ref = request.args.get('show_ref', 'true').lower() != 'false'

    try:
        from app.models.quote import QuoteItem
        items = QuoteItem.query.filter_by(quote_id=id).order_by(
            QuoteItem.category_level1, QuoteItem.sort_order
        ).all()
        if not items:
            return jsonify({'code': 400, 'message': 'No items found'}), 400

        from app.utils.pdf_generator import generate_quote_pdf
        rel_path = generate_quote_pdf(quote, items, is_visitor=False, show_ref=show_ref)

        upload_root = Path(__file__).parent.parent.parent / 'upload'
        pdf_dir = upload_root / 'pdf'
        fname = rel_path.replace('pdf/', '')
        return send_from_directory(pdf_dir, fname, as_attachment=True)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'code': 500, 'message': str(e)}), 500


@quote_bp.route('/<int:id>/pdf-customer', methods=['GET'])
@jwt_required_v2
def download_pdf_customer(current_user, id):
    """下载报价PDF（客户版，无水印）"""
    from flask import send_from_directory
    from pathlib import Path

    quote = Quote.query.get_or_404(id)

    upload_root = Path(__file__).parent.parent.parent / 'upload'
    pdf_dir = upload_root / 'pdf'

    pattern = f'quote_{quote.quote_no}_customer_*.pdf'
    import glob as _glob
    files = sorted(_glob.glob(str(pdf_dir / pattern)), reverse=True)

    if not files:
        return jsonify({'code': 404, 'message': 'PDF文件不存在，请先生成'}), 404

    file_path = Path(files[0])
    if not str(file_path.resolve()).startswith(str(pdf_dir.resolve())):
        return jsonify({'code': 403, 'message': '非法文件路径'}), 403

    return send_from_directory(pdf_dir, file_path.name, as_attachment=True)


@quote_bp.route('/<int:id>/generate-pdf', methods=['POST'])
@jwt_required_v2
def generate_pdf(current_user, id):
    """手动重新生成报价PDF（双版本）"""
    quote = Quote.query.get_or_404(id)

    try:
        from app.utils.pdf_generator import generate_both_pdfs
        from flask import request
        show_ref = request.args.get('show_ref', 'true').lower() != 'false'
        pdf_result = generate_both_pdfs(id, show_ref=show_ref)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'code': 500, 'message': 'PDF generation failed: {}'.format(str(e))}), 500

    if not pdf_result:
        return jsonify({'code': 400, 'message': 'No items found for this quote'}), 400

    return jsonify({
        'code': 200,
        'message': 'PDF generated',
        'data': pdf_result
    })


@quote_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_quote(current_user, id):
    """删除报价"""
    quote = Quote.query.get_or_404(id)
    quote.is_deleted = True
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


# ========== 报价项管理 ==========

@quote_bp.route('/<int:quote_id>/items', methods=['POST'])
@jwt_required_v2
def add_item(current_user, quote_id):
    """添加报价项"""
    data = request.get_json()

    w = data.get('width')
    d = data.get('depth')
    h = data.get('height')
    unit = data.get('unit', '项')
    m_val = calc_measurement_value(
        unit, width=w, depth=d, height=h,
        manual_value=data.get('measurement_value'),
        category_level2=data.get('category_level2'),
        custom_name=data.get('custom_name'),
        material_name=data.get('name'),
        process_name=data.get('process_name')
    )

    item = QuoteItem(
        quote_id=quote_id,
        custom_name=data.get('custom_name'),
        room_name=data.get('room_name'),
        category_level1=data.get('category_level1'),
        category_level2=data.get('category_level2'),
        category_level3=data.get('category_level3'),
        item_type=data.get('item_type', 'product'),
        sku_id=data.get('sku_id'),
        name=data.get('name'),
        spec=data.get('spec'),
        brand=data.get('brand'),
        material=data.get('material'),
        unit=unit,
        calc_type=data.get('calc_type'),
        quantity=data.get('quantity', 1),
        unit_price=data.get('unit_price', 0),
        width=w,
        depth=d,
        height=h,
        measurement_value=m_val,
        custom_width=data.get('custom_width'),
        custom_depth=data.get('custom_depth'),
        custom_height=data.get('custom_height'),
        custom_result=data.get('custom_result'),
        process_name=data.get('process_name'),
        process_coefficient=data.get('process_coefficient', 1),
        process_quantity=data.get('process_quantity', 0),
        process_unit=data.get('process_unit'),
        process_unit_price=data.get('process_unit_price', 0),
        process_amount=data.get('process_amount', 0),
        craft_type=data.get('craft_type'),
        craft_price=data.get('craft_price', 0),
        craft_quantity=data.get('craft_quantity', 1),
        craft_coefficient=data.get('craft_coefficient', 1),
        image=data.get('image'),
        remark=data.get('remark')
    )
    item.total_price = calc_item_total_price(item)

    db.session.add(item)
    db.session.commit()
    _recalculate_quote_total(quote_id)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': item.to_dict()
    })


@quote_bp.route('/<int:quote_id>/items/<int:item_id>', methods=['PUT'])
@jwt_required_v2
def update_item(current_user, quote_id, item_id):
    """更新报价项"""
    item = QuoteItem.query.get_or_404(item_id)
    data = request.get_json()

    fields = ['custom_name', 'room_name', 'category_level1', 'category_level2', 'category_level3',
              'name', 'spec', 'brand', 'material', 'unit', 'calc_type', 'quantity', 'unit_price',
              'process_name', 'process_coefficient', 'process_quantity',
              'process_unit', 'process_unit_price', 'process_amount',
              'craft_type', 'craft_price', 'image', 'remark',
              'width', 'depth', 'height',
              'custom_width', 'custom_depth', 'custom_height', 'custom_result']

    for field in fields:
        if field in data:
            setattr(item, field, data[field])

    # 重新计算计量值
    item.measurement_value = calc_measurement_value(
        item.unit, width=item.width, depth=item.depth, height=item.height,
        manual_value=data.get('measurement_value'),
        category_level2=item.category_level2,
        custom_name=item.custom_name,
        material_name=item.name,
        process_name=item.process_name
    )
    # 更新 craft 字段
    if 'craft_quantity' in data:
        item.craft_quantity = data['craft_quantity']
    if 'craft_coefficient' in data:
        item.craft_coefficient = data['craft_coefficient']
    # 重新计算总价
    item.total_price = calc_item_total_price(item)

    db.session.commit()
    _recalculate_quote_total(quote_id)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': item.to_dict()
    })


@quote_bp.route('/<int:quote_id>/items/<int:item_id>', methods=['DELETE'])
@jwt_required_v2
def delete_item(current_user, quote_id, item_id):
    """删除报价项"""
    item = QuoteItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    _recalculate_quote_total(quote_id)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


# ========== 统计报表 ==========

@quote_bp.route('/statistics', methods=['GET'])
@jwt_required_v2
def get_statistics(current_user):
    """获取报价统计"""
    tenant_id = current_user.get('tenant_id', '0')

    # 状态统计
    status_stats = db.session.query(
        Quote.status,
        db.func.count(Quote.id)
    ).filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).group_by(Quote.status).all()

    # 金额统计
    amount_stats = db.session.query(
        db.func.sum(Quote.total_amount)
    ).filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).first()

    # 本月新增
    current_month = date.today().replace(day=1)
    new_this_month = Quote.query.filter(
        Quote.tenant_id == tenant_id,
        Quote.is_deleted == False,
        Quote.created_at >= current_month
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'by_status': {s: c for s, c in status_stats},
            'total_amount': float(amount_stats[0]) if amount_stats[0] else 0,
            'new_this_month': new_this_month
        }
    })


# ========== 选项数据 ==========

@quote_bp.route('/options', methods=['GET'])
@jwt_required_v2
def get_options(current_user):
    """获取报价相关选项"""
    # 获取员工列表（用于服务团队选择）
    employees = Employee.query.filter_by(
        status='active'
    ).all()

    employee_options = [{
        'id': e.id,
        'name': e.name,
        'phone': e.phone,
        'department_id': e.department_id,
        'position_id': e.position_id
    } for e in employees]

    return jsonify({
        'code': 200,
        'data': {
            'categories': [{'value': v, 'label': l} for v, l in QUOTE_CATEGORIES],
            'service_roles': [{'value': v, 'label': l} for v, l in SERVICE_ROLES],
            'rooms': ROOM_OPTIONS,
            'status_list': [{'value': v, 'label': l} for v, l in QUOTE_STATUS],
            'employees': employee_options
        }
    })


# ========== 从物料库导入 ==========

@quote_bp.route('/import-from-sku', methods=['POST'])
@jwt_required_v2
def import_from_sku(current_user):
    """从物料库导入到报价"""
    data = request.get_json()
    sku_ids = data.get('sku_ids', [])

    from app.models.material_sku import MaterialSKU

    items = []
    for sku_id in sku_ids:
        sku = MaterialSKU.query.get(sku_id)
        if sku:
            items.append({
                'sku_id': sku.id,
                'name': sku.name,
                'spec': sku.spec,
                'brand': sku.brand,
                'unit': sku.unit,
                'unit_price': float(sku.base_price) if sku.base_price else 0,
                'image': sku.images[0] if sku.images else None,
                'category_level1': sku.category_name,
            })

    return jsonify({
        'code': 200,
        'data': items
    })


# ========== Phase 2: 从案例模板克隆报价 ==========

@quote_bp.route('/preview-clone', methods=['POST'])
@jwt_required_v2
def preview_clone(current_user):
    """
    克隆预览 - 不创建报价，仅返回预览数据
    
    输入: {
        case_id: 案例ID,
        selected_configs: [{space_type, config_id, version_level}],
        adjustments: [{sku_id, action: 'add'|'remove'|'replace', ...}]
    }
    """
    from app.models.space_config import CaseSpaceConfig, CaseSpaceConfigItem
    from app.models.case import CaseStudy
    
    data = request.get_json()
    case_id = data.get('case_id')
    selected_configs = data.get('selected_configs', [])
    adjustments = data.get('adjustments', [])
    
    # 获取案例
    case = CaseStudy.query.get_or_404(case_id)
    
    # 构建预览数据
    preview = {
        'case_id': case_id,
        'case_title': case.title,
        'case_style': case.style,
        'spaces': [],
        'summary': {
            'total_material_cost': 0,
            'total_labor_cost': 0,
            'total_design_cost': 0,
            'total_manage_cost': 0,
            'grand_total': 0
        }
    }
    
    selected_config_ids = []
    
    for sel in selected_configs:
        space_type = sel.get('space_type')
        config_id = sel.get('config_id')
        version_level = sel.get('version_level', '舒适')
        
        # 查找配置
        if config_id:
            config = CaseSpaceConfig.query.get(config_id)
        else:
            # 按空间类型和版本查找
            config = CaseSpaceConfig.query.filter_by(
                case_id=case_id,
                space_type=space_type,
                version_level=version_level,
                is_template=True,
                status='active'
            ).first()
        
        if not config:
            continue
            
        selected_config_ids.append(config.id)
        
        # 获取配置明细
        items = CaseSpaceConfigItem.query.filter_by(config_id=config.id).all()
        
        space_data = {
            'config_id': config.id,
            'space_type': config.space_type,
            'space_name': config.space_name or config.space_type,
            'space_area': float(config.space_area) if config.space_area else None,
            'version_level': config.version_level,
            'version_code': config.version_code,
            'original_price': float(config.total_price) if config.total_price else 0,
            'adjusted_price': float(config.total_price) if config.total_price else 0,
            'items': []
        }
        
        # 处理物料明细
        for item in items:
            item_data = item.to_dict()
            item_data['is_adjusted'] = False
            space_data['items'].append(item_data)
            
            # 累计汇总
            preview['summary']['total_material_cost'] += float(item.total_price or 0)
        
        # 累计费用
        preview['summary']['total_labor_cost'] += float(config.labor_cost or 0)
        preview['summary']['total_design_cost'] += float(config.design_cost or 0)
        preview['summary']['total_manage_cost'] += float(config.manage_cost or 0)
        
        preview['spaces'].append(space_data)
    
    # 应用调整项
    adjustment_log = []
    for adj in adjustments:
        result = _apply_adjustment(preview, adj)
        if result:
            adjustment_log.append(result)
    
    # 重新计算总价
    preview['summary']['grand_total'] = (
        preview['summary']['total_material_cost'] +
        preview['summary']['total_labor_cost'] +
        preview['summary']['total_design_cost'] +
        preview['summary']['total_manage_cost']
    )
    
    return jsonify({
        'code': 200,
        'data': {
            'preview': preview,
            'adjustment_log': adjustment_log,
            'selected_config_ids': selected_config_ids
        }
    })


@quote_bp.route('/clone-from-template', methods=['POST'])
@jwt_required_v2
def clone_from_template(current_user):
    """
    从案例模板克隆报价
    
    输入: {
        case_id: 案例ID,
        customer_id: 客户ID,
        selected_configs: [{space_type, config_id, version_level}],
        adjustments: [{...}],
        service_team: [...],
        cover_config: {...},
        remark: '...'
    }
    """
    from app.models.space_config import CaseSpaceConfig, CaseSpaceConfigItem, QuoteSpaceInstance
    from app.models.case import CaseStudy
    import json
    
    data = request.get_json()
    
    # 验证必填项
    case_id = data.get('case_id')
    customer_id = data.get('customer_id')
    
    if not case_id or not customer_id:
        return jsonify({'code': 400, 'message': '缺少案例ID或客户ID'}), 400
    
    case = CaseStudy.query.get_or_404(case_id)
    customer = Customer.query.get_or_404(customer_id)
    
    # 生成报价编号
    today = date.today().strftime('%Y%m%d')
    count = Quote.query.filter(
        Quote.quote_no.like(f'BJ{today}%')
    ).count()
    quote_no = f"BJ{today}{count+1:04d}"
    
    # 创建报价单
    valid_days = data.get('valid_days', 30)
    
    quote = Quote(
        tenant_id=current_user.get('tenant_id', '0'),
        quote_no=quote_no,
        customer_id=customer_id,
        cover_config=data.get('cover_config', {}),
        service_team=data.get('service_team', []),
        status='draft',
        valid_days=valid_days,
        expire_date=date.today() + timedelta(days=valid_days),
        creator_id=current_user.get('id'),
        creator_name=current_user.get('name'),
        remark=data.get('remark')
    )
    
    db.session.add(quote)
    db.session.flush()  # 获取quote.id
    
    selected_configs = data.get('selected_configs', [])
    adjustments = data.get('adjustments', [])
    
    total_material_cost = 0
    total_labor_cost = 0
    total_design_cost = 0
    total_manage_cost = 0
    
    # 处理每个空间配置
    for sel in selected_configs:
        space_type = sel.get('space_type')
        config_id = sel.get('config_id')
        version_level = sel.get('version_level', '舒适')
        
        # 查找配置模板
        if config_id:
            template = CaseSpaceConfig.query.get(config_id)
        else:
            template = CaseSpaceConfig.query.filter_by(
                case_id=case_id,
                space_type=space_type,
                version_level=version_level,
                is_template=True,
                status='active'
            ).first()
        
        if not template:
            continue
        
        # 创建空间实例
        instance = QuoteSpaceInstance(
            tenant_id=current_user.get('tenant_id', '0'),
            quote_id=quote.id,
            template_config_id=template.id,
            space_type=template.space_type,
            space_name=template.space_name or template.space_type,
            space_area=template.space_area,
            version_level=template.version_level,
            original_price=template.total_price,
            adjusted_price=template.total_price,
            is_selected=True
        )
        
        db.session.add(instance)
        db.session.flush()
        
        # 复制物料明细到报价项
        template_items = CaseSpaceConfigItem.query.filter_by(config_id=template.id).all()
        
        for template_item in template_items:
            quote_item = QuoteItem(
                quote_id=quote.id,
                room_name=template.space_type,
                item_type='product',
                sku_id=template_item.sku_id,
                name=template_item.sku_name,
                spec=template_item.specification,
                brand=template_item.brand,
                unit=template_item.unit,
                quantity=float(template_item.quantity or 1),
                unit_price=float(template_item.unit_price or 0),
                sort_order=template_item.sort_order
            )
            quote_item.total_price = calc_item_total_price(quote_item)
            db.session.add(quote_item)
            total_material_cost += float(quote_item.total_price or 0)
        
        total_labor_cost += float(template.labor_cost or 0)
        total_design_cost += float(template.design_cost or 0)
        total_manage_cost += float(template.manage_cost or 0)
    
    # 应用调整项
    for adj in adjustments:
        _apply_adjustment_to_quote(quote.id, adj)
    
    # 更新报价汇总
    quote.subtotal = total_material_cost
    quote.management_fee = total_manage_cost
    quote.total_amount = total_material_cost + total_labor_cost + total_design_cost + total_manage_cost
    
    # 用 recalculate 统一汇总（覆盖上面的手工计算）
    _recalculate_quote_total(quote.id)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '克隆成功',
        'data': quote.to_dict(include_items=True)
    })


@quote_bp.route('/calculate', methods=['POST'])
@jwt_required_v2
def calculate_quote(current_user):
    """
    实时计价
    
    输入: {
        spaces: [{
            config_id, version_level, items: [{sku_id, quantity, unit_price, ...}]
        }],
        apply_management_fee: true,
        management_fee_rate: 8,
        apply_tax: false,
        tax_rate: 6
    }
    """
    from app.models.space_config import CaseSpaceConfig, CaseSpaceConfigItem
    
    data = request.get_json()
    spaces = data.get('spaces', [])
    apply_management_fee = data.get('apply_management_fee', True)
    management_fee_rate = data.get('management_fee_rate', 8)
    apply_tax = data.get('apply_tax', False)
    tax_rate = data.get('tax_rate', 6)
    
    result = {
        'spaces': [],
        'subtotal': 0,
        'management_fee': 0,
        'tax': 0,
        'total': 0
    }
    
    for space in spaces:
        config_id = space.get('config_id')
        version_level = space.get('version_level', '舒适')
        items = space.get('items', [])
        
        space_total = 0
        space_data = {
            'config_id': config_id,
            'version_level': version_level,
            'items': [],
            'subtotal': 0,
            'labor_cost': 0,
            'design_cost': 0,
            'manage_cost': 0,
            'total': 0
        }
        
        # 如果有config_id，获取模板基础费用
        if config_id:
            config = CaseSpaceConfig.query.get(config_id)
            if config:
                space_data['labor_cost'] = float(config.labor_cost or 0)
                space_data['design_cost'] = float(config.design_cost or 0)
                space_data['manage_cost'] = float(config.manage_cost or 0)
        
        # 计算物料费用
        for item in items:
            quantity = float(item.get('quantity', 1))
            unit_price = float(item.get('unit_price', 0))
            item_total = quantity * unit_price
            
            space_data['items'].append({
                'sku_id': item.get('sku_id'),
                'name': item.get('name'),
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': item_total
            })
            space_total += item_total
        
        space_data['subtotal'] = space_total
        space_data['total'] = space_total + space_data['labor_cost'] + space_data['design_cost'] + space_data['manage_cost']
        
        result['spaces'].append(space_data)
        result['subtotal'] += space_data['total']
    
    # 计算管理费
    if apply_management_fee:
        result['management_fee'] = round(result['subtotal'] * management_fee_rate / 100, 2)
    
    # 计算税费
    base_amount = result['subtotal'] + result['management_fee']
    if apply_tax:
        result['tax'] = round(base_amount * tax_rate / 100, 2)
    
    result['total'] = result['subtotal'] + result['management_fee'] + result['tax']
    
    return jsonify({
        'code': 200,
        'data': result
    })


@quote_bp.route('/<int:id>/space-instances', methods=['GET'])
@jwt_required_v2
def get_space_instances(current_user, id):
    """获取报价单的空间配置实例"""
    from app.models.space_config import QuoteSpaceInstance
    
    instances = QuoteSpaceInstance.query.filter_by(
        quote_id=id,
        is_selected=True
    ).all()
    
    return jsonify({
        'code': 200,
        'data': [inst.to_dict() for inst in instances]
    })


@quote_bp.route('/<int:id>/space-instances', methods=['POST'])
@jwt_required_v2
def create_space_instance(current_user, id):
    """创建空间配置实例"""
    from app.models.space_config import QuoteSpaceInstance

    quote = Quote.query.get_or_404(id)
    data = request.get_json()
    space_name = data.get('space_name', '').strip()
    if not space_name:
        return jsonify({'code': 400, 'message': '空间名称不能为空'}), 400

    tenant_id = current_user.get('tenant_id', '0')
    instance = QuoteSpaceInstance(
        quote_id=id,
        tenant_id=tenant_id,
        space_type=data.get('space_type', 'custom'),
        space_name=space_name,
        space_area=data.get('space_area', 0),
        version_level=data.get('version_level', 'standard'),
        original_price=0,
        adjusted_price=0,
        is_selected=True
    )
    db.session.add(instance)
    db.session.commit()
    db.session.refresh(instance)
    return jsonify({
        'code': 200,
        'message': '空间创建成功',
        'data': instance.to_dict()
    })


@quote_bp.route('/<int:quote_id>/space-instances/<int:instance_id>/items', methods=['GET'])
@jwt_required_v2
def get_space_items(current_user, quote_id, instance_id):
    """获取空间实例的物料列表"""
    from app.models.space_config import QuoteSpaceInstance
    from app.models.quote import QuoteItem
    
    # 验证空间实例存在且属于该报价
    instance = QuoteSpaceInstance.query.filter_by(id=instance_id, quote_id=quote_id).first_or_404()
    
    items = QuoteItem.query.filter_by(quote_id=quote_id, space_name=instance.space_name).all()
    
    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': [item.to_dict() for item in items]
    })


@quote_bp.route('/<int:quote_id>/space-instances/<int:instance_id>/items', methods=['POST'])
@jwt_required_v2
def add_item_to_space_instance(current_user, quote_id, instance_id):
    """向空间实例添加物料项"""
    from app.models.space_config import QuoteSpaceInstance
    
    # 验证空间实例存在且属于该报价
    instance = QuoteSpaceInstance.query.filter_by(id=instance_id, quote_id=quote_id).first_or_404()
    
    data = request.get_json()
    
    w = data.get('width')
    d = data.get('depth')
    h = data.get('height')
    unit = data.get('unit', '项')
    m_val = calc_measurement_value(
        unit, width=w, depth=d, height=h,
        manual_value=data.get('measurement_value'),
        category_level2=data.get('category_level2'),
        custom_name=data.get('custom_name'),
        material_name=data.get('name'),
        process_name=data.get('process_name')
    )
    
    item = QuoteItem(
        quote_id=quote_id,
        room_name=instance.space_name or instance.space_type,
        category_level1=data.get('category_level1'),
        category_level2=data.get('category_level2'),
        category_level3=data.get('category_level3'),
        item_type=data.get('item_type', 'product'),
        sku_id=data.get('sku_id'),
        name=data.get('name'),
        spec=data.get('spec'),
        brand=data.get('brand'),
        material=data.get('material'),
        unit=unit,
        calc_type=data.get('calc_type'),
        quantity=data.get('quantity', 1),
        unit_price=data.get('unit_price', 0),
        width=w,
        depth=d,
        height=h,
        measurement_value=m_val,
        custom_width=data.get('custom_width'),
        custom_depth=data.get('custom_depth'),
        custom_height=data.get('custom_height'),
        custom_result=data.get('custom_result'),
        process_name=data.get('process_name'),
        process_coefficient=data.get('process_coefficient', 1),
        process_quantity=data.get('process_quantity', 0),
        process_unit=data.get('process_unit'),
        process_unit_price=data.get('process_unit_price', 0),
        process_amount=data.get('process_amount', 0),
        craft_type=data.get('craft_type'),
        craft_price=data.get('craft_price', 0),
        craft_quantity=data.get('craft_quantity', 1),
        craft_coefficient=data.get('craft_coefficient', 1),
        image=data.get('image'),
        remark=data.get('remark')
    )
    item.total_price = calc_item_total_price(item)
    
    db.session.add(item)
    db.session.commit()
    _recalculate_quote_total(quote_id)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': item.to_dict()
    })


@quote_bp.route('/<int:quote_id>/space-instances/<int:instance_id>/items/<int:item_id>', methods=['PUT'])
@jwt_required_v2
def update_space_item(current_user, quote_id, instance_id, item_id):
    """更新空间实例中的物料项"""
    from app.models.space_config import QuoteSpaceInstance
    
    # 验证空间实例存在且属于该报价
    instance = QuoteSpaceInstance.query.filter_by(id=instance_id, quote_id=quote_id).first_or_404()
    item = QuoteItem.query.get_or_404(item_id)
    
    if item.quote_id != quote_id:
        return jsonify({'code': 404, 'message': '物料不属于该报价'}), 404
    
    data = request.get_json()
    
    fields = ['custom_name', 'room_name', 'category_level1', 'category_level2', 'category_level3',
              'name', 'spec', 'brand', 'material', 'unit', 'calc_type', 'quantity', 'unit_price',
              'process_name', 'process_coefficient', 'process_quantity',
              'process_unit', 'process_unit_price', 'process_amount',
              'craft_type', 'craft_price', 'image', 'remark',
              'width', 'depth', 'height',
              'custom_width', 'custom_depth', 'custom_height', 'custom_result']
    
    for field in fields:
        if field in data:
            setattr(item, field, data[field])
    
    # 自动计算计量值（基于输入参数，默认为0）
    item.measurement_value = calc_measurement_value(
        item.unit,
        width=item.width or item.custom_width,
        depth=item.depth or item.custom_depth,
        height=item.height or item.custom_height,
        manual_value=data.get('measurement_value'),
        category_level2=item.category_level2,
        custom_name=item.custom_name,
        material_name=item.name,
        process_name=item.process_name
    )
    
    # 更新工艺字段
    if 'craft_quantity' in data:
        item.craft_quantity = data['craft_quantity']
    if 'craft_coefficient' in data:
        item.craft_coefficient = data['craft_coefficient']
    
    # 重新计算总价
    item.total_price = calc_item_total_price(item)
    
    db.session.commit()
    _recalculate_quote_total(quote_id)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': item.to_dict()
    })


@quote_bp.route('/<int:quote_id>/space-instances/<int:instance_id>/items/<int:item_id>', methods=['DELETE'])
@jwt_required_v2
def delete_space_item(current_user, quote_id, instance_id, item_id):
    """删除空间实例中的物料项"""
    from app.models.space_config import QuoteSpaceInstance
    
    instance = QuoteSpaceInstance.query.filter_by(id=instance_id, quote_id=quote_id).first_or_404()
    item = QuoteItem.query.get_or_404(item_id)
    
    if item.quote_id != quote_id:
        return jsonify({'code': 404, 'message': '物料不属于该报价'}), 404
    
    db.session.delete(item)
    db.session.commit()
    _recalculate_quote_total(quote_id)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '删除成功'})


@quote_bp.route('/<int:id>/space-instances/<int:instance_id>', methods=['DELETE'])
@jwt_required_v2
def delete_space_instance(current_user, id, instance_id):
    """删除空间配置实例"""
    from app.models.space_config import QuoteSpaceInstance

    instance = QuoteSpaceInstance.query.filter_by(
        id=instance_id, quote_id=id
    ).first_or_404()
    db.session.delete(instance)
    db.session.commit()
    return jsonify({'code': 200, 'message': '空间删除成功'})


@quote_bp.route('/<int:id>/space-instances/<int:instance_id>', methods=['PUT'])
@jwt_required_v2
def update_space_instance(current_user, id, instance_id):
    """更新空间配置实例（调整价格或物料）"""
    from app.models.space_config import QuoteSpaceInstance
    
    instance = QuoteSpaceInstance.query.filter_by(
        id=instance_id,
        quote_id=id
    ).first_or_404()
    
    data = request.get_json()
    
    # 更新调整价格
    if 'adjusted_price' in data:
        instance.adjusted_price = data['adjusted_price']
    if 'adjustment_reason' in data:
        instance.adjustment_reason = data['adjustment_reason']
    if 'adjustments' in data:
        import json
        instance.adjustments = json.dumps(data['adjustments'], ensure_ascii=False)
    
    # 重新计算报价总价
    _recalculate_quote_total(id)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': instance.to_dict()
    })


@quote_bp.route('/check-exclusive-conflicts', methods=['POST'])
@jwt_required_v2
def check_exclusive_conflicts(current_user):
    """
    检查互斥冲突
    
    输入: {
        selected_sku_ids: [1, 2, 3],
        new_sku_id: 4
    }
    """
    from app.models.space_config import MaterialExclusiveRule
    import json
    
    data = request.get_json()
    selected_sku_ids = data.get('selected_sku_ids', [])
    new_sku_id = data.get('new_sku_id')
    
    if not new_sku_id:
        return jsonify({'code': 200, 'data': {'has_conflict': False}})
    
    # 获取所有涉及物料的互斥规则
    all_sku_ids = set(selected_sku_ids + [new_sku_id])
    
    rules = MaterialExclusiveRule.query.filter(
        MaterialExclusiveRule.sku_id.in_(all_sku_ids),
        MaterialExclusiveRule.is_enabled == True,
        MaterialExclusiveRule.tenant_id.in_([current_user.get('tenant_id', '0'), '0'])
    ).all()
    
    conflicts = []
    for rule in rules:
        exclusive_ids = set(json.loads(rule.exclusive_sku_ids) if rule.exclusive_sku_ids else [])
        
        # 检查新添加的物料是否与已选物料冲突
        if rule.sku_id == new_sku_id:
            conflicting = set(selected_sku_ids) & exclusive_ids
            if conflicting:
                conflicts.append({
                    'rule_id': rule.id,
                    'rule_name': rule.rule_name,
                    'conflicting_sku_ids': list(conflicting)
                })
        else:
            # 检查已选物料中是否有与新物料互斥的
            if rule.sku_id in selected_sku_ids and new_sku_id in exclusive_ids:
                conflicts.append({
                    'rule_id': rule.id,
                    'rule_name': rule.rule_name,
                    'conflicting_sku_ids': [rule.sku_id]
                })
    
    return jsonify({
        'code': 200,
        'data': {
            'has_conflict': len(conflicts) > 0,
            'conflicts': conflicts
        }
    })


# ========== 辅助函数 ==========

def _apply_adjustment(preview, adjustment):
    """应用调整项到预览数据"""
    action = adjustment.get('action')
    space_type = adjustment.get('space_type')
    sku_id = adjustment.get('sku_id')
    
    for space in preview['spaces']:
        if space_type and space['space_type'] != space_type:
            continue
            
        if action == 'remove':
            space['items'] = [item for item in space['items'] if item.get('sku_id') != sku_id]
            space['adjusted_price'] = sum(item['total_price'] for item in space['items'])
            return {'action': 'remove', 'sku_id': sku_id, 'space_type': space_type}
            
        elif action == 'add':
            new_item = {
                'sku_id': adjustment.get('sku_id'),
                'name': adjustment.get('name'),
                'quantity': adjustment.get('quantity', 1),
                'unit_price': adjustment.get('unit_price', 0),
                'total_price': adjustment.get('quantity', 1) * adjustment.get('unit_price', 0),
                'is_adjusted': True
            }
            space['items'].append(new_item)
            space['adjusted_price'] += new_item['total_price']
            return {'action': 'add', 'sku_id': sku_id, 'space_type': space_type}
            
        elif action == 'modify':
            for item in space['items']:
                if item.get('sku_id') == sku_id:
                    if 'quantity' in adjustment:
                        item['quantity'] = adjustment['quantity']
                        item['total_price'] = item['quantity'] * item['unit_price']
                    if 'unit_price' in adjustment:
                        item['unit_price'] = adjustment['unit_price']
                        item['total_price'] = item['quantity'] * item['unit_price']
                    item['is_adjusted'] = True
                    space['adjusted_price'] = sum(it['total_price'] for it in space['items'])
                    return {'action': 'modify', 'sku_id': sku_id, 'space_type': space_type}
    
    return None


def _apply_adjustment_to_quote(quote_id, adjustment):
    """应用调整项到实际报价"""
    action = adjustment.get('action')
    space_type = adjustment.get('space_type')
    sku_id = adjustment.get('sku_id')
    
    if action == 'remove':
        QuoteItem.query.filter_by(
            quote_id=quote_id,
            room_name=space_type,
            sku_id=sku_id
        ).delete()
        
    elif action == 'add':
        item = QuoteItem(
            quote_id=quote_id,
            room_name=space_type,
            sku_id=sku_id,
            name=adjustment.get('name'),
            quantity=adjustment.get('quantity', 1),
            unit_price=adjustment.get('unit_price', 0),
            total_price=adjustment.get('quantity', 1) * adjustment.get('unit_price', 0)
        )
        db.session.add(item)
        
    elif action == 'modify':
        item = QuoteItem.query.filter_by(
            quote_id=quote_id,
            room_name=space_type,
            sku_id=sku_id
        ).first()
        if item:
            if 'quantity' in adjustment:
                item.quantity = adjustment['quantity']
                item.total_price = item.quantity * item.unit_price
            if 'unit_price' in adjustment:
                item.unit_price = adjustment['unit_price']
                item.total_price = item.quantity * item.unit_price


def _build_category_summary(quote_id):
    """构建分类汇总 — 自动从物料项汇总"""
    items = QuoteItem.query.filter_by(quote_id=quote_id).all()

    # 分类名称映射
    cat_name_map = dict(QUOTE_CATEGORIES)

    summary = {}
    for item in items:
        cat = item.category_level1 or 'other'
        if cat not in summary:
            summary[cat] = {
                'name': cat_name_map.get(cat, cat),
                'amount': 0,
                'count': 0
            }
        summary[cat]['amount'] += float(item.total_price or 0)
        summary[cat]['count'] += 1

    return summary  # 返回dict


def _recalculate_quote_total(quote_id):
    """重新计算报价总价 — 自动汇总subtotal/category_summary/total_amount"""
    quote = Quote.query.get(quote_id)
    if not quote:
        return

    # 1. 计算所有报价项总价之和
    items_total = db.session.query(
        db.func.sum(QuoteItem.total_price)
    ).filter_by(quote_id=quote_id).scalar() or 0

    # 2. 构建分类汇总
    category_summary = _build_category_summary(quote_id)

    # 3. 更新报价
    quote.subtotal = items_total
    quote.category_summary = category_summary
    # total_amount = subtotal + management_fee + tax
    mgmt_fee = float(quote.management_fee or 0)
    tax = float(quote.tax or 0)
    quote.total_amount = float(items_total) + mgmt_fee + tax


# ========== 预览 / 复制 / 批量 ==========

@quote_bp.route('/<int:id>/preview', methods=['GET'])
@jwt_required_v2
def preview_quote(current_user, id):
    """获取报价预览数据 — 同房间同商品分组(category_level2)合并，子项展开

    合并规则：
    - 同一 room_name 下，按 category_level2 分组（如"柜体"）
    - 若无 category_level2，则按 name 分组
    - 每个分组显示子项明细（如柜体板/背板/挂衣杆/拉篮）
    - item_type 为 service 的不合并，独立显示
    """
    quote = Quote.query.get_or_404(id)
    items = QuoteItem.query.filter_by(quote_id=id).order_by(
        QuoteItem.room_name, QuoteItem.category_level2, QuoteItem.sort_order
    ).all()

    # 按房间分组，同房间内按 category_level2（或 name）分组
    rooms_dict = {}
    for item in items:
        room = item.room_name or '\u672a\u6307\u5b9a'
        if room not in rooms_dict:
            rooms_dict[room] = {}

        # 决定分组键：service 独立，否则按 category_level2 或 name
        if item.item_type == 'service':
            # 服务项独立显示，用唯一键
            group_key = f"_svc_{item.id}"
            group_name = item.name or '\u672a\u547d\u540d'
        else:
            group_key = item.category_level2 or item.name or '\u672a\u547d\u540d'
            group_name = group_key

        if group_key not in rooms_dict[room]:
            rooms_dict[room][group_key] = {
                'name': group_name,
                'category_level1': item.category_level1,
                'category_level2': item.category_level2,
                'item_count': 0,
                'total_price': 0,
                'items': [],
                'is_service': item.item_type == 'service'
            }
        rooms_dict[room][group_key]['item_count'] += 1
        rooms_dict[room][group_key]['total_price'] += float(item.total_price or 0)
        rooms_dict[room][group_key]['items'].append(item.to_dict())

    # 转为列表
    rooms = []
    for room_name, groups in rooms_dict.items():
        room_total = sum(g['total_price'] for g in groups.values())
        rooms.append({
            'room_name': room_name,
            'groups': list(groups.values()),
            'room_total': room_total
        })

    # 客户信息
    customer = Customer.query.get(quote.customer_id)

    return jsonify({
        'code': 200,
        'data': {
            'quote': quote.to_dict(),
            'customer': customer.to_dict() if customer else None,
            'rooms': rooms,
            'category_summary': quote.category_summary or {},
            'subtotal': float(quote.subtotal or 0),
            'management_fee': float(quote.management_fee or 0),
            'tax': float(quote.tax or 0),
            'total_amount': float(quote.total_amount or 0)
        }
    })


@quote_bp.route('/<int:id>/duplicate', methods=['POST'])
@jwt_required_v2
def duplicate_quote(current_user, id):
    """复制报价单"""
    quote = Quote.query.get_or_404(id)

    # 生成新编号
    today = date.today().strftime('%Y%m%d')
    count = Quote.query.filter(
        Quote.quote_no.like(f'BJ{today}%')
    ).count()
    quote_no = f"BJ{today}{count+1:04d}"

    # 深拷贝报价单
    new_quote = Quote(
        tenant_id=current_user.get('tenant_id', '0'),
        quote_no=quote_no,
        customer_id=quote.customer_id,
        customer_name=quote.customer_name,
        customer_phone=quote.customer_phone,
        cover_config=quote.cover_config or {},
        service_team=quote.service_team or [],
        category_summary={},  # 将由 recalculate 自动计算
        subtotal=0,
        management_fee=quote.management_fee,
        management_fee_rate=quote.management_fee_rate,
        tax=quote.tax,
        tax_rate=quote.tax_rate,
        total_amount=0,
        status='draft',
        valid_days=quote.valid_days,
        expire_date=date.today() + timedelta(days=quote.valid_days or 30),
        creator_id=current_user.get('id'),
        creator_name=current_user.get('name'),
        remark=quote.remark
    )
    db.session.add(new_quote)
    db.session.flush()

    # 深拷贝物料项
    old_items = QuoteItem.query.filter_by(quote_id=id).all()
    for old_item in old_items:
        new_item = QuoteItem(
            quote_id=new_quote.id,
            room_name=old_item.room_name,
            category_level1=old_item.category_level1,
            category_level2=old_item.category_level2,
            category_level3=old_item.category_level3,
            item_type=old_item.item_type,
            sku_id=old_item.sku_id,
            name=old_item.name,
            spec=old_item.spec,
            brand=old_item.brand,
            unit=old_item.unit,
            quantity=old_item.quantity,
            unit_price=old_item.unit_price,
            width=old_item.width,
            depth=old_item.depth,
            height=old_item.height,
            measurement_value=old_item.measurement_value,
            total_price=old_item.total_price,
            craft_type=old_item.craft_type,
            craft_price=old_item.craft_price,
            craft_quantity=old_item.craft_quantity,
            craft_coefficient=old_item.craft_coefficient,
            image=old_item.image,
            remark=old_item.remark,
            sort_order=old_item.sort_order,
            tenant_id=getattr(old_item, 'tenant_id', current_user.get('tenant_id', '0'))
        )
        db.session.add(new_item)

    db.session.commit()
    _recalculate_quote_total(new_quote.id)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '复制成功',
        'data': new_quote.to_dict(include_items=True)
    })


@quote_bp.route('/<int:quote_id>/items/batch', methods=['POST'])
@jwt_required_v2
def batch_add_items(current_user, quote_id):
    """批量添加报价项"""
    data = request.get_json()
    items_data = data.get('items', [])

    if not items_data:
        return jsonify({'code': 400, 'message': '没有物料项'}), 400

    added = []
    for item_data in items_data:
        w = item_data.get('width')
        d = item_data.get('depth')
        h = item_data.get('height')
        unit = item_data.get('unit', '项')
        m_val = calc_measurement_value(
            unit, width=w, depth=d, height=h,
            manual_value=item_data.get('measurement_value'),
            category_level2=item_data.get('category_level2'),
            custom_name=item_data.get('custom_name'),
            material_name=item_data.get('name'),
            process_name=item_data.get('process_name')
        )
        item = QuoteItem(
            quote_id=quote_id,
            room_name=item_data.get('room_name'),
            category_level1=item_data.get('category_level1'),
            category_level2=item_data.get('category_level2'),
            category_level3=item_data.get('category_level3'),
            item_type=item_data.get('item_type', 'product'),
            sku_id=item_data.get('sku_id'),
            name=item_data.get('name'),
            spec=item_data.get('spec'),
            brand=item_data.get('brand'),
            unit=unit,
            quantity=item_data.get('quantity', 1),
            unit_price=item_data.get('unit_price', 0),
            width=w,
            depth=d,
            height=h,
            measurement_value=m_val,
            craft_type=item_data.get('craft_type'),
            craft_price=item_data.get('craft_price', 0),
            craft_quantity=item_data.get('craft_quantity', 1),
            craft_coefficient=item_data.get('craft_coefficient', 1),
            image=item_data.get('image'),
            remark=item_data.get('remark'),
            sort_order=item_data.get('sort_order', 0)
        )
        item.total_price = calc_item_total_price(item)
        db.session.add(item)
        added.append(item)

    db.session.commit()
    _recalculate_quote_total(quote_id)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '批量添加成功',
        'data': {
            'added_count': len(added),
            'items': [item.to_dict() for item in added]
        }
    })


@quote_bp.route('/<int:id>/recalculate', methods=['POST'])
@jwt_required_v2
def manual_recalculate(current_user, id):
    """手动触发重新计算报价"""
    quote = Quote.query.get_or_404(id)

    # 重新计算所有物料项的 total_price
    items = QuoteItem.query.filter_by(quote_id=id).all()
    for item in items:
        item.measurement_value = calc_measurement_value(
            item.unit, width=item.width, depth=item.depth, height=item.height,
            manual_value=item.measurement_value if float(item.measurement_value or 0) != 1 else None,
            category_level2=item.category_level2,
            custom_name=item.custom_name,
            material_name=item.name,
            process_name=item.process_name
        )
        item.total_price = calc_item_total_price(item)

    db.session.commit()
    _recalculate_quote_total(id)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '重新计算完成',
        'data': quote.to_dict(include_items=True)
    })


# ========== 报价费用构成解析（合同导入用） ==========

# 七大类费用映射规则
FEE_CATEGORIES = {
    # key: (中文名, 匹配的category_level1值列表, 对应合同字段)
    'design_fee':        ('全案服务费',    ['design'],                                     'design_fee'),
    'hard_material':     ('硬装材料费',    ['hard_material', 'Hard Material'],             'material_fee'),
    'construction':      ('硬装施工费',    ['construction', 'Construction'],               'construction_fee'),
    'custom_furniture':  ('全屋定制家具',  ['custom', 'Custom Furniture'],                  None),  # 合并到 material_fee
    'finished_furniture':('成品家具',      ['furniture', 'Finished Furniture'],             None),  # 合并到 soft_fee
    'soft_decor':        ('软装饰品',      ['soft', 'Soft Decor'],                         'soft_fee'),
    'other':             ('其他费用',      [],                                             None),   # 兜底
}


@quote_bp.route('/<int:id>/fee-breakdown', methods=['GET'])
@jwt_required_v2
def get_quote_fee_breakdown(current_user, id):
    """解析报价单的费用构成，按七大类汇总

    用于合同模块导入报价表时自动识别费用分布
    返回：
    - categories: 七大类各自金额和明细
    - totals: 各合同字段的建议填充值
    - items: 每个物料项的分类归属
    """
    quote = Quote.query.get_or_404(id)
    items = QuoteItem.query.filter_by(quote_id=id).order_by(QuoteItem.sort_order, QuoteItem.id).all()
    
    # 初始化七大类
    breakdown = {
        'design_fee':        {'name': '全案服务费',     'amount': 0, 'items': [], 'contract_field': 'design_fee'},
        'hard_material':     {'name': '硬装材料费',     'amount': 0, 'items': [], 'contract_field': 'material_fee'},
        'construction':      {'name': '硬装施工费',     'amount': 0, 'items': [], 'contract_field': 'construction_fee'},
        'custom_furniture':  {'name': '全屋定制家具',   'amount': 0, 'items': [], 'contract_field': 'custom_furniture_fee'},
        'finished_furniture':{'name': '成品家具',       'amount': 0, 'items': [], 'contract_field': 'furniture_fee'},
        'soft_decor':        {'name': '软装饰品',       'amount': 0, 'items': [], 'contract_field': 'soft_fee'},
        'other':             {'name': '其他费用',       'amount': 0, 'items': [], 'contract_field': None},
    }
    
    # 分类映射：category_level1 -> 七大类key
    cat_mapping = {
        'design':              'design_fee',
        'Design':              'design_fee',
        'hard_material':       'hard_material',
        'Hard Material':       'hard_material',
        'construction':        'construction',
        'Construction':        'construction',
        'custom':              'custom_furniture',
        'Custom Furniture':    'custom_furniture',
        'furniture':           'finished_furniture',
        'Finished Furniture':  'finished_furniture',
        'soft':                'soft_decor',
        'Soft Decor':          'soft_decor',
        'Soft':                'soft_decor',
    }
    
    total = 0
    for item in items:
        price = float(item.total_price or 0)
        total += price
        
        # 确定分类
        cat_l1 = (item.category_level1 or '').strip()
        category_key = cat_mapping.get(cat_l1, 'other')
        
        item_info = {
            'id': item.id,
            'name': item.name,
            'category_level1': cat_l1,
            'category_level2': item.category_level2 or '',
            'room_name': item.room_name or '',
            'quantity': float(item.quantity or 1),
            'unit_price': float(item.unit_price or 0),
            'total_price': price,
            'assigned_category': category_key,
        }
        
        breakdown[category_key]['items'].append(item_info)
        breakdown[category_key]['amount'] += price
    
    # 四舍五入
    for k in breakdown:
        breakdown[k]['amount'] = round(breakdown[k]['amount'], 2)
    
    # 计算合同字段建议值（合并策略）
    contract_suggestion = {
        'total_amount': round(total, 2),
        'design_fee': round(breakdown['design_fee']['amount'], 2),
        'construction_fee': round(breakdown['construction']['amount'] + breakdown['hard_material']['amount'], 2),  # 施工+材料
        'material_fee': round(breakdown['hard_material']['amount'], 2),  # 单独硬装材料
        'custom_furniture_fee': round(breakdown['custom_furniture']['amount'], 2),
        'furniture_fee': round(breakdown['finished_furniture']['amount'], 2),
        'soft_fee': round(breakdown['soft_decor']['amount'] + breakdown['finished_furniture']['amount'], 2),  # 软装+成品家具
        'other_fee': round(breakdown['other']['amount'], 2),
    }
    
    return jsonify({
        'code': 200,
        'data': {
            'quote_id': id,
            'quote_no': quote.quote_no,
            'customer_name': quote.customer_name,
            'item_count': len(items),
            'total_amount': round(total, 2),
            'breakdown': {k: {'name': v['name'], 'amount': v['amount'], 'count': len(v['items'])} for k, v in breakdown.items()},
            'detail_items': {k: v['items'] for k, v in breakdown.items() if v['items']},
            'contract_suggestion': contract_suggestion,
        }
    })


# ========== V3.2 报价工作流 ==========

@quote_bp.route('/<int:id>/submit', methods=['POST'])
@jwt_required_v2
def submit_quote(current_user, id):
    from app.routes.auth_routes_v2 import jwt_required_v2
    quote = Quote.query.get_or_404(id)
    
    if quote.created_by != current_user.id and current_user.role != 'admin':
        return jsonify({'code': 403, 'message': 'no permission'}), 403
    
    if not quote.customer_name or not quote.customer_phone:
        return jsonify({'code': 400, 'message': 'incomplete customer info'}), 400
    
    if not quote.items:
        return jsonify({'code': 400, 'message': 'no items'}), 400
    
    quote.status = 'pending'
    db.session.commit()
    
    return jsonify({'code': 200, 'message': 'submitted', 'data': {'quote_id': id, 'status': 'pending'}})


@quote_bp.route('/<int:id>/approve', methods=['POST'])
@jwt_required_v2
def approve_quote(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'code': 403, 'message': 'admin only'}), 403
    
    quote = Quote.query.get_or_404(id)
    data = request.get_json() or {}
    
    quote.status = 'approved'
    quote.approved_by = current_user.id
    quote.approval_note = data.get('note', '')
    
    if data.get('seal_url'):
        quote.seal_url = data['seal_url']
    
    db.session.commit()
    
    return jsonify({'code': 200, 'message': 'approved', 'data': {'quote_id': id, 'status': 'approved'}})


@quote_bp.route('/<int:id>/reject', methods=['POST'])
@jwt_required_v2
def reject_quote(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'code': 403, 'message': 'admin only'}), 403
    
    quote = Quote.query.get_or_404(id)
    data = request.get_json() or {}
    reason = data.get('reason', '')
    
    if not reason:
        return jsonify({'code': 400, 'message': 'reason required'}), 400
    
    quote.status = 'rejected'
    quote.approved_by = current_user.id
    quote.approval_note = reason
    db.session.commit()
    
    return jsonify({'code': 200, 'message': 'rejected', 'data': {'quote_id': id, 'status': 'rejected'}})


@quote_bp.route('/import', methods=['POST'])
@jwt_required_v2
def import_quote(current_user):
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': 'no file'}), 400
    
    file = request.files['file']
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'code': 400, 'message': 'excel only'}), 400
    
    try:
        import pandas as pd
        df = pd.read_excel(file)
        
        items = []
        for _, row in df.iterrows():
            items.append({
                'space_name': str(row.get('space_name', '')),
                'sku_code': str(row.get('sku_code', '')),
                'custom_name': str(row.get('custom_name', '')),
                'material_name': str(row.get('material_name', '')),
                'quantity': float(row.get('quantity', 1)),
                'unit_price': float(row.get('unit_price', 0)),
            })
        
        return jsonify({'code': 200, 'message': f'parsed {len(items)} items', 'data': {'items': items}})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


# ========== 计量规则管理 ==========

@quote_bp.route('/measurement-rules', methods=['GET'])
@jwt_required_v2
def get_measurement_rules(current_user):
    """获取计量规则列表"""
    rules = MeasurementRule.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_deleted=False
    ).order_by(MeasurementRule.priority.asc(), MeasurementRule.sort_order.asc()).all()
    return jsonify({'code': 200, 'data': [r.to_dict() for r in rules]})


@quote_bp.route('/measurement-rules/init', methods=['POST'])
@jwt_required_v2
def init_measurement_rules(current_user):
    """初始化默认计量规则（仅在无规则时创建）"""
    tenant_id = current_user.get('tenant_id', '0')
    existing = MeasurementRule.query.filter_by(tenant_id=tenant_id).first()
    if existing:
        return jsonify({'code': 200, 'message': '规则已存在', 'data': {'count': MeasurementRule.query.filter_by(tenant_id=tenant_id).count()}})
    for r in DEFAULT_MEASUREMENT_RULES:
        rule = MeasurementRule(
            tenant_id=tenant_id,
            name=r['name'],
            description=r['description'],
            match_type=r['match_type'],
            match_value=r['match_value'],
            match_field=r['match_field'],
            rule_type=r['rule_type'],
            rule_params=r['rule_params'],
            priority=r['priority'],
            is_enabled=True,
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )
        db.session.add(rule)
    db.session.commit()
    return jsonify({'code': 200, 'message': f'已初始化{len(DEFAULT_MEASUREMENT_RULES)}条规则'})


@quote_bp.route('/measurement-rules', methods=['POST'])
@jwt_required_v2
def create_measurement_rule(current_user):
    """创建计量规则"""
    data = request.get_json()
    rule = MeasurementRule(
        tenant_id=current_user.get('tenant_id', '0'),
        name=data.get('name', ''),
        description=data.get('description', ''),
        match_type=data.get('match_type', 'keyword_category'),
        match_value=data.get('match_value', ''),
        match_field=data.get('match_field', 'unit'),
        rule_type=data.get('rule_type', 'length'),
        rule_params=data.get('rule_params', {}),
        priority=data.get('priority', 100),
        sort_order=data.get('sort_order', 0),
        is_enabled=data.get('is_enabled', True),
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify({'code': 200, 'message': '创建成功', 'data': rule.to_dict()})


@quote_bp.route('/measurement-rules/<int:rule_id>', methods=['PUT'])
@jwt_required_v2
def update_measurement_rule(current_user, rule_id):
    """更新计量规则"""
    rule = MeasurementRule.query.get_or_404(rule_id)
    data = request.get_json()
    for field in ['name', 'description', 'match_type', 'match_value', 'match_field',
                  'rule_type', 'rule_params', 'priority', 'sort_order', 'is_enabled']:
        if field in data:
            setattr(rule, field, data[field])
    rule.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.session.commit()
    return jsonify({'code': 200, 'message': '更新成功', 'data': rule.to_dict()})


@quote_bp.route('/measurement-rules/<int:rule_id>', methods=['DELETE'])
@jwt_required_v2
def delete_measurement_rule(current_user, rule_id):
    """删除计量规则"""
    rule = MeasurementRule.query.get_or_404(rule_id)
    rule.is_deleted = True
    db.session.commit()
    return jsonify({'code': 200, 'message': '已删除'})
