"""
合同管理模块 - API路由
V3.0 全新设计
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.contract import (
    Contract, ContractTemplate, ContractPayment, ContractChange,
    CONTRACT_TYPES, CONTRACT_STATUS, PAYMENT_PHASES
)
from app.models.customer import Customer
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime, date

contract_bp = Blueprint('contract', __name__, url_prefix='/api/v3/contracts')


# ========== 合同模板 ==========

@contract_bp.route('/templates', methods=['GET'])
@jwt_required_v2
def get_templates(current_user):
    """获取合同模板列表"""
    contract_type = request.args.get('contract_type')

    query = ContractTemplate.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_enabled=True
    )

    if contract_type:
        query = query.filter_by(contract_type=contract_type)

    templates = query.order_by(ContractTemplate.sort_order).all()

    return jsonify({
        'code': 200,
        'data': [t.to_dict() for t in templates]
    })


@contract_bp.route('/templates', methods=['POST'])
@jwt_required_v2
@jwt_required_v2
def create_template(current_user):
    """创建合同模板"""
    data = request.get_json()

    template = ContractTemplate(
        tenant_id=current_user.get('tenant_id', '0'),
        name=data['name'],
        code=data.get('code'),
        contract_type=data['contract_type'],
        content=data.get('content', ''),
        variables=data.get('variables', []),
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


@contract_bp.route('/templates/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_template(current_user, id):
    """更新合同模板"""
    template = ContractTemplate.query.get_or_404(id)
    data = request.get_json()

    fields = ['name', 'code', 'contract_type', 'content', 'variables', 'is_default', 'is_enabled']
    for field in fields:
        if field in data:
            setattr(template, field, data[field])

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': template.to_dict()
    })


# ========== 合同管理 ==========

@contract_bp.route('', methods=['GET'])
@jwt_required_v2
def get_contracts(current_user):
    """获取合同列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    customer_id = request.args.get('customer_id', type=int)
    status = request.args.get('status')
    contract_type = request.args.get('contract_type')

    query = Contract.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_deleted=False
    )

    if keyword:
        query = query.filter(
            db.or_(
                Contract.contract_no.contains(keyword),
                Contract.title.contains(keyword)
            )
        )

    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if status:
        query = query.filter_by(status=status)
    if contract_type:
        query = query.filter_by(contract_type=contract_type)

    query = query.order_by(Contract.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 加载客户信息
    items = []
    for contract in pagination.items:
        data = contract.to_dict()
        customer = Customer.query.get(contract.customer_id)
        data['customer_name'] = customer.name if customer else None
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


@contract_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
def get_contract(current_user, id):
    """获取合同详情"""
    contract = Contract.query.get_or_404(id)

    # 加载付款记录
    payments = ContractPayment.query.filter_by(contract_id=id).order_by(ContractPayment.planned_date).all()

    # 加载变更记录
    changes = ContractChange.query.filter_by(contract_id=id).order_by(ContractChange.created_at.desc()).all()

    data = contract.to_dict(include_content=True)
    data['payments'] = [p.to_dict() for p in payments]
    data['changes'] = [c.to_dict() for c in changes]

    # 客户信息
    customer = Customer.query.get(contract.customer_id)
    data['customer'] = customer.to_dict() if customer else None

    return jsonify({
        'code': 200,
        'data': data
    })


@contract_bp.route('', methods=['POST'])
@jwt_required_v2
def create_contract(current_user):
    """创建合同"""
    data = request.get_json()

    # 生成合同编号
    today = date.today().strftime('%Y%m%d')
    count = Contract.query.filter(
        Contract.contract_no.like(f'HT{today}%')
    ).count()
    contract_no = f"HT{today}{count+1:04d}"

    # 处理付款计划
    payment_schedule = data.get('payment_schedule', [])
    for item in payment_schedule:
        item['status'] = 'pending'

    contract = Contract(
        tenant_id=current_user.get('tenant_id', '0'),
        contract_no=contract_no,
        customer_id=data['customer_id'],
        template_id=data.get('template_id'),
        contract_type=data.get('contract_type'),
        title=data.get('title', f'合同-{contract_no}'),
        content=data.get('content', ''),
        variables=data.get('variables', {}),
        total_amount=data.get('total_amount', 0),
        design_fee=data.get('design_fee', 0),
        construction_fee=data.get('construction_fee', 0),
        material_fee=data.get('material_fee', 0),
        soft_fee=data.get('soft_fee', 0),
        payment_schedule=payment_schedule,
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        status='draft',
        creator_id=current_user.get('id'),
        manager_id=data.get('manager_id'),
        remark=data.get('remark')
    )

    db.session.add(contract)
    db.session.flush()

    # 创建付款记录
    for item in payment_schedule:
        payment = ContractPayment(
            contract_id=contract.id,
            phase=item.get('phase'),
            percentage=item.get('percentage', 0),
            amount=item.get('amount', 0),
            planned_date=item.get('planned_date'),
            status='pending'
        )
        db.session.add(payment)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_contract(current_user, id):
    """更新合同"""
    contract = Contract.query.get_or_404(id)
    data = request.get_json()

    # 只有草稿状态可以修改基本信息
    if contract.status == 'draft':
        fields = ['title', 'content', 'variables', 'total_amount', 'design_fee',
                  'construction_fee', 'material_fee', 'soft_fee', 'start_date',
                  'end_date', 'manager_id', 'remark']
        for field in fields:
            if field in data:
                setattr(contract, field, data[field])

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>/submit', methods=['POST'])
@jwt_required_v2
def submit_contract(current_user, id):
    """提交合同（草稿->待签署）"""
    contract = Contract.query.get_or_404(id)

    if contract.status != 'draft':
        return jsonify({'code': 400, 'message': '只有草稿状态可以提交'}), 400

    contract.status = 'pending'
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '提交成功',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>/sign', methods=['POST'])
@jwt_required_v2
def sign_contract(current_user, id):
    """签署合同"""
    contract = Contract.query.get_or_404(id)
    data = request.get_json()

    signer = data.get('signer')  # customer/company

    if signer == 'customer':
        contract.signed_by_customer = True
        contract.customer_sign_date = datetime.utcnow()
    elif signer == 'company':
        contract.signed_by_company = True
        contract.company_sign_date = datetime.utcnow()

    # 双方都签署后，状态变为已签署
    if contract.signed_by_customer and contract.signed_by_company:
        contract.status = 'signed'
        contract.signed_date = date.today()

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '签署成功',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>/execute', methods=['POST'])
@jwt_required_v2
def execute_contract(current_user, id):
    """开始执行合同"""
    contract = Contract.query.get_or_404(id)

    if contract.status != 'signed':
        return jsonify({'code': 400, 'message': '合同未签署'}), 400

    contract.status = 'executing'
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '已开始执行',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>/complete', methods=['POST'])
@jwt_required_v2
def complete_contract(current_user, id):
    """完成合同"""
    contract = Contract.query.get_or_404(id)

    contract.status = 'completed'
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '合同已完成',
        'data': contract.to_dict()
    })


@contract_bp.route('/<int:id>/cancel', methods=['POST'])
@jwt_required_v2
def cancel_contract(current_user, id):
    """取消合同"""
    contract = Contract.query.get_or_404(id)
    data = request.get_json()

    contract.status = 'cancelled'

    # 记录变更
    change = ContractChange(
        contract_id=id,
        change_type='cancel',
        old_value={'status': contract.status},
        new_value={'status': 'cancelled'},
        reason=data.get('reason'),
        operator_id=current_user.get('id')
    )
    db.session.add(change)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '合同已取消',
        'data': contract.to_dict()
    })


# ========== 付款管理 ==========

@contract_bp.route('/<int:contract_id>/payments/<int:payment_id>/pay', methods=['POST'])
@jwt_required_v2
def record_payment(current_user, contract_id, payment_id):
    """记录付款"""
    payment = ContractPayment.query.get_or_404(payment_id)
    data = request.get_json()

    payment.status = 'paid'
    payment.actual_date = data.get('actual_date') or date.today()
    payment.payment_method = data.get('payment_method')
    payment.transaction_no = data.get('transaction_no')
    payment.receipt_url = data.get('receipt_url')
    payment.remark = data.get('remark')

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '付款记录成功',
        'data': payment.to_dict()
    })


# ========== 统计报表 ==========

@contract_bp.route('/statistics', methods=['GET'])
@jwt_required_v2
def get_statistics(current_user):
    """获取合同统计"""
    tenant_id = current_user.get('tenant_id', '0')

    # 状态统计
    status_stats = db.session.query(
        Contract.status,
        db.func.count(Contract.id)
    ).filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).group_by(Contract.status).all()

    # 类型统计
    type_stats = db.session.query(
        Contract.contract_type,
        db.func.count(Contract.id)
    ).filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).group_by(Contract.contract_type).all()

    # 金额统计
    amount_stats = db.session.query(
        db.func.sum(Contract.total_amount)
    ).filter_by(
        tenant_id=tenant_id,
        is_deleted=False
    ).first()

    # 本月新增
    current_month = date.today().replace(day=1)
    new_this_month = Contract.query.filter(
        Contract.tenant_id == tenant_id,
        Contract.is_deleted == False,
        Contract.created_at >= current_month
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'by_status': {s: c for s, c in status_stats},
            'by_type': {t: c for t, c in type_stats},
            'total_amount': float(amount_stats[0]) if amount_stats[0] else 0,
            'new_this_month': new_this_month
        }
    })


# ========== 选项数据 ==========

@contract_bp.route('/options', methods=['GET'])
@jwt_required_v2
def get_options(current_user):
    """获取合同相关选项"""
    return jsonify({
        'code': 200,
        'data': {
            'contract_types': [{'value': v, 'label': l} for v, l in CONTRACT_TYPES],
            'status_list': [{'value': v, 'label': l} for v, l in CONTRACT_STATUS],
            'payment_phases': [{'value': v, 'label': l} for v, l in PAYMENT_PHASES],
        }
    })
