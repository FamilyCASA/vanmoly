"""
客户管理模块 - API路由
从 vanmoly-distilled 蒸馏而来
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.customer import Customer, CustomerFollow, CUSTOMER_SOURCES, CUSTOMER_TYPES, CUSTOMER_STATUS, PRIORITY_OPTIONS, FOLLOW_TYPES
from app.routes.auth_routes_v2 import jwt_required_v2
from app.services.permission_service import require_permission
from datetime import datetime

customer_bp = Blueprint('customer', __name__, url_prefix='/api/v3/customers')


def _store_scope(current_user, *args, **kwargs):
    return 'store', current_user.get('store_id')


@customer_bp.route('', methods=['GET'])
@jwt_required_v2
@require_permission('customer.view', _store_scope)
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

    # 批量加载关联数据：workflow进度、报价、合同、案例、方案、财务、项目组
    from app.models.service_workflow import CustomerWorkflow
    from app.models.quote import Quote
    from app.models.contract import Contract
    from app.models.hr import Employee
    from app.models.case import CaseStudy
    from app.models.scheme import CustomerScheme
    from app.models.finance import FinanceTransaction, FinanceReceivable
    from app.models.project_team import ProjectTeam

    customer_ids = [c.id for c in pagination.items]
    customer_phones = [c.phone for c in pagination.items if c.phone]

    # 1. workflow 进度
    workflows = CustomerWorkflow.query.filter(
        CustomerWorkflow.customer_id.in_(customer_ids),
        CustomerWorkflow.is_deleted == False
    ).all()
    workflow_map = {}
    for w in workflows:
        existing = workflow_map.get(w.customer_id)
        if not existing or (w.status == 'active' and existing.status != 'active'):
            workflow_map[w.customer_id] = w
        elif w.status == 'active' and existing.status == 'active':
            if w.updated_at and existing.updated_at and w.updated_at > existing.updated_at:
                workflow_map[w.customer_id] = w

    # 2. 报价统计
    quotes = Quote.query.filter(Quote.customer_id.in_(customer_ids)).all()
    quote_count_map = {}
    quote_amount_map = {}
    latest_quote_map = {}
    for q in quotes:
        quote_count_map[q.customer_id] = quote_count_map.get(q.customer_id, 0) + 1
        if q.status in ('approved', 'signed'):
            quote_amount_map[q.customer_id] = quote_amount_map.get(q.customer_id, 0) + (q.total_amount or 0)
        if q.customer_id not in latest_quote_map or (q.created_at and latest_quote_map[q.customer_id].created_at and q.created_at > latest_quote_map[q.customer_id].created_at):
            latest_quote_map[q.customer_id] = q

    # 3. 合同统计
    contracts = Contract.query.filter(Contract.customer_id.in_(customer_ids)).all()
    contract_count_map = {}
    contract_amount_map = {}
    latest_contract_map = {}
    for ct in contracts:
        contract_count_map[ct.customer_id] = contract_count_map.get(ct.customer_id, 0) + 1
        contract_amount_map[ct.customer_id] = contract_amount_map.get(ct.customer_id, 0) + (ct.total_amount or 0)
        if ct.customer_id not in latest_contract_map or (ct.signed_date and latest_contract_map[ct.customer_id].signed_date and ct.signed_date > latest_contract_map[ct.customer_id].signed_date):
            latest_contract_map[ct.customer_id] = ct

    # 4. 案例统计
    cases = CaseStudy.query.filter(CaseStudy.customer_id.in_(customer_ids)).all()
    case_count_map = {}
    latest_case_map = {}
    for cs in cases:
        case_count_map[cs.customer_id] = case_count_map.get(cs.customer_id, 0) + 1
        if cs.customer_id not in latest_case_map or (cs.created_at and latest_case_map[cs.customer_id].created_at and cs.created_at > latest_case_map[cs.customer_id].created_at):
            latest_case_map[cs.customer_id] = cs

    # 5. 方案统计
    schemes = CustomerScheme.query.filter(CustomerScheme.customer_id.in_(customer_ids)).all()
    scheme_count_map = {}
    scheme_amount_map = {}
    latest_scheme_map = {}
    for s in schemes:
        scheme_count_map[s.customer_id] = scheme_count_map.get(s.customer_id, 0) + 1
        scheme_amount_map[s.customer_id] = scheme_amount_map.get(s.customer_id, 0) + (s.total_amount or 0)
        if s.customer_id not in latest_scheme_map or (s.created_at and latest_scheme_map[s.customer_id].created_at and s.created_at > latest_scheme_map[s.customer_id].created_at):
            latest_scheme_map[s.customer_id] = s

    # 6. 财务流水统计（收款/付款）
    transactions = FinanceTransaction.query.filter(
        FinanceTransaction.customer_id.in_(customer_ids)
    ).all()
    income_map = {}
    expense_map = {}
    for t in transactions:
        if t.trans_type == 'income':
            income_map[t.customer_id] = income_map.get(t.customer_id, 0) + (t.amount or 0)
        elif t.trans_type == 'expense':
            expense_map[t.customer_id] = expense_map.get(t.customer_id, 0) + (t.amount or 0)

    # 7. 应收款统计
    receivables = FinanceReceivable.query.filter(
        FinanceReceivable.customer_id.in_(customer_ids)
    ).all()
    receivable_total_map = {}
    received_total_map = {}
    remaining_total_map = {}
    for r in receivables:
        receivable_total_map[r.customer_id] = receivable_total_map.get(r.customer_id, 0) + (r.amount or 0)
        received_total_map[r.customer_id] = received_total_map.get(r.customer_id, 0) + (r.received_amount or 0)
        remaining_total_map[r.customer_id] = remaining_total_map.get(r.customer_id, 0) + (r.remaining_amount or 0)

    # 8. 项目组统计
    projects = ProjectTeam.query.filter(
        ProjectTeam.related_customer_id.in_(customer_ids),
        ProjectTeam.is_deleted == False
    ).all()
    project_count_map = {}
    active_project_map = {}
    for p in projects:
        project_count_map[p.related_customer_id] = project_count_map.get(p.related_customer_id, 0) + 1
        if p.status not in ('completed', 'cancelled', 'closed'):
            active_project_map[p.related_customer_id] = active_project_map.get(p.related_customer_id, 0) + 1

    # 9. 预约统计（通过手机号关联）
    from app.models.appointment import Appointment
    appointments = Appointment.query.filter(Appointment.phone.in_(customer_phones)).all() if customer_phones else []
    appt_count_map = {}
    latest_appt_map = {}
    # 建立 phone -> customer_id 映射
    phone_to_cid = {c.phone: c.id for c in pagination.items if c.phone}
    for a in appointments:
        cid = phone_to_cid.get(a.phone)
        if not cid:
            continue
        appt_count_map[cid] = appt_count_map.get(cid, 0) + 1
        if cid not in latest_appt_map or (a.created_at and latest_appt_map[cid].created_at and a.created_at > latest_appt_map[cid].created_at):
            latest_appt_map[cid] = a

    # 10. owner_name
    owner_ids = list(set(c.owner_id for c in pagination.items if c.owner_id))
    owner_map = {}
    if owner_ids:
        employees = Employee.query.filter(Employee.id.in_(owner_ids)).all()
        owner_map = {e.id: e.name for e in employees}

    # 组装数据
    items = []
    for c in pagination.items:
        item = c.to_dict()
        wf = workflow_map.get(c.id)
        if wf:
            item['workflow'] = {
                'status': wf.status,
                'current_node_name': wf.current_node.node_name if wf.current_node else None,
                'current_phase': wf.current_phase,
                'progress_pct': round(wf.completed_nodes / wf.total_nodes * 100, 1) if wf.total_nodes else 0,
                'completed_nodes': wf.completed_nodes,
                'total_nodes': wf.total_nodes,
            }
        else:
            item['workflow'] = None
        item['quote_count'] = quote_count_map.get(c.id, 0)
        item['quote_total_amount'] = round(quote_amount_map.get(c.id, 0), 2)
        item['latest_quote_no'] = latest_quote_map[c.id].quote_no if c.id in latest_quote_map else None
        item['contract_count'] = contract_count_map.get(c.id, 0)
        item['contract_total_amount'] = round(contract_amount_map.get(c.id, 0), 2)
        item['latest_contract_no'] = latest_contract_map[c.id].contract_no if c.id in latest_contract_map else None
        item['latest_contract_date'] = latest_contract_map[c.id].signed_date.isoformat() if c.id in latest_contract_map and latest_contract_map[c.id].signed_date else None
        item['case_count'] = case_count_map.get(c.id, 0)
        item['latest_case_title'] = latest_case_map[c.id].title if c.id in latest_case_map else None
        item['latest_case_type'] = latest_case_map[c.id].type if c.id in latest_case_map else None
        item['scheme_count'] = scheme_count_map.get(c.id, 0)
        item['scheme_total_amount'] = round(scheme_amount_map.get(c.id, 0), 2)
        item['latest_scheme_no'] = latest_scheme_map[c.id].scheme_no if c.id in latest_scheme_map else None
        item['income_total'] = round(income_map.get(c.id, 0), 2)
        item['expense_total'] = round(expense_map.get(c.id, 0), 2)
        item['receivable_total'] = round(receivable_total_map.get(c.id, 0), 2)
        item['received_total'] = round(received_total_map.get(c.id, 0), 2)
        item['remaining_receivable'] = round(remaining_total_map.get(c.id, 0), 2)
        item['project_count'] = project_count_map.get(c.id, 0)
        item['active_project_count'] = active_project_map.get(c.id, 0)
        item['appointment_count'] = appt_count_map.get(c.id, 0)
        latest_appt = latest_appt_map.get(c.id)
        if latest_appt:
            item['latest_appointment_date'] = latest_appt.appointment_date.isoformat() if latest_appt.appointment_date else None
            item['latest_appointment_status'] = latest_appt.status
        else:
            item['latest_appointment_date'] = None
            item['latest_appointment_status'] = None
        item['owner_name'] = owner_map.get(c.owner_id, None)
        items.append(item)

    return jsonify({
        'code': 200,
        'data': {
            'items': items,
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@customer_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
@require_permission('customer.view', _store_scope)
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
@require_permission('customer.create', _store_scope)
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
@require_permission('customer.update', _store_scope)
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
@require_permission('customer.delete', _store_scope)
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
@require_permission('customer.update', _store_scope)
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
@require_permission('customer.view', _store_scope)
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

