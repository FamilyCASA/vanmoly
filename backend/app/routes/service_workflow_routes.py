"""
服务流程模块 - API路由
58节点全案服务流程
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.service_workflow import (
    WorkflowNode, CustomerWorkflow, WorkflowNodeRecord,
    PHASES, NODES_DEFINITION
)
from app.models.customer import Customer
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime

service_workflow_bp = Blueprint('service_workflow', __name__, url_prefix='/api/v3/workflows')


# ========== 节点定义管理 ==========

@service_workflow_bp.route('/nodes', methods=['GET'])
@jwt_required_v2
def get_nodes(current_user):
    """获取所有节点定义"""
    phase = request.args.get('phase')

    query = WorkflowNode.query.filter_by(is_enabled=True)
    if phase:
        query = query.filter_by(phase=phase)

    nodes = query.order_by(WorkflowNode.phase_order).all()

    # 按阶段分组
    result = {}
    for phase_info in PHASES:
        result[phase_info['code']] = {
            'info': phase_info,
            'nodes': []
        }

    for node in nodes:
        if node.phase in result:
            result[node.phase]['nodes'].append(node.to_dict())

    return jsonify({
        'code': 200,
        'data': result
    })


@service_workflow_bp.route('/nodes/init', methods=['POST'])
@jwt_required_v2
def init_nodes(current_user):
    """初始化58节点（首次使用）"""
    # 检查是否已初始化
    existing = WorkflowNode.query.first()
    if existing:
        return jsonify({'code': 400, 'message': '节点已初始化'}), 400

    for i, node_def in enumerate(NODES_DEFINITION, 1):
        node = WorkflowNode(
            node_code=node_def['code'],
            node_name=node_def['name'],
            phase=node_def['phase'],
            phase_order=i,
            description=node_def.get('description', ''),
            responsible_roles=node_def['roles'],
            related_module=node_def.get('module'),
            finance_trigger=node_def.get('finance') is not None,
            finance_type=node_def.get('finance'),
            is_enabled=True,
            sort_order=i
        )
        db.session.add(node)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '初始化成功',
        'data': {'total': len(NODES_DEFINITION)}
    })


@service_workflow_bp.route('/phases', methods=['GET'])
@jwt_required_v2
def get_phases(current_user):
    """获取阶段定义"""
    return jsonify({
        'code': 200,
        'data': PHASES
    })


# ========== 客户流程实例 ==========

@service_workflow_bp.route('', methods=['GET'])
@jwt_required_v2
def get_workflows(current_user):
    """获取客户流程列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    customer_id = request.args.get('customer_id', type=int)
    status = request.args.get('status')
    phase = request.args.get('phase')

    query = CustomerWorkflow.query.filter_by(is_deleted=False)

    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if status:
        query = query.filter_by(status=status)
    if phase:
        query = query.filter_by(current_phase=phase)

    query = query.order_by(CustomerWorkflow.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [w.to_dict() for w in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@service_workflow_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
def get_workflow(current_user, id):
    """获取流程详情"""
    workflow = CustomerWorkflow.query.get_or_404(id)
    return jsonify({
        'code': 200,
        'data': workflow.to_dict(include_records=True)
    })


@service_workflow_bp.route('', methods=['POST'])
@jwt_required_v2
def create_workflow(current_user):
    """为客户创建流程"""
    data = request.get_json()
    customer_id = data['customer_id']

    # 检查客户是否存在
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'code': 404, 'message': '客户不存在'}), 404

    # 检查是否已有活跃流程
    existing = CustomerWorkflow.query.filter_by(
        customer_id=customer_id,
        status='active',
        is_deleted=False
    ).first()
    if existing:
        return jsonify({'code': 400, 'message': '该客户已有进行中的流程'}), 400

    # 获取第一个节点
    first_node = WorkflowNode.query.filter_by(
        node_code='N01', is_enabled=True
    ).first()

    workflow = CustomerWorkflow(
        tenant_id=current_user.get('tenant_id', '0'),
        customer_id=customer_id,
        current_node_id=first_node.id if first_node else None,
        current_phase='acquisition',
        status='active',
        start_date=data.get('start_date'),
        planned_end_date=data.get('planned_end_date'),
        total_nodes=58,
        completed_nodes=0
    )

    db.session.add(workflow)
    db.session.flush()

    # 创建第一个节点的记录
    if first_node:
        record = WorkflowNodeRecord(
            workflow_id=workflow.id,
            node_id=first_node.id,
            status='pending',
            deadline=data.get('first_node_deadline')
        )
        db.session.add(record)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '流程创建成功',
        'data': workflow.to_dict()
    })


@service_workflow_bp.route('/<int:id>/advance', methods=['POST'])
@jwt_required_v2
def advance_workflow(current_user, id):
    """推进到下一节点"""
    workflow = CustomerWorkflow.query.get_or_404(id)
    data = request.get_json()

    # 完成当前节点
    current_record = WorkflowNodeRecord.query.filter_by(
        workflow_id=id,
        node_id=workflow.current_node_id,
        status='processing'
    ).first()

    if current_record:
        current_record.status = 'completed'
        current_record.completed_at = datetime.utcnow()
        current_record.executed_by = current_user.get('id')
        current_record.content = data.get('content', '')
        current_record.attachments = data.get('attachments', [])

        workflow.completed_nodes += 1

    # 查找下一节点
    current_node = WorkflowNode.query.get(workflow.current_node_id)
    next_node = WorkflowNode.query.filter(
        WorkflowNode.phase_order > current_node.phase_order,
        WorkflowNode.is_enabled == True
    ).order_by(WorkflowNode.phase_order).first()

    if next_node:
        workflow.current_node_id = next_node.id
        workflow.current_phase = next_node.phase

        # 创建新节点记录
        new_record = WorkflowNodeRecord(
            workflow_id=workflow.id,
            node_id=next_node.id,
            status='pending',
            deadline=data.get('next_deadline')
        )
        db.session.add(new_record)

        # 更新客户状态
        customer = Customer.query.get(workflow.customer_id)
        if customer:
            customer.status = f'flow_{next_node.phase}'
    else:
        # 流程完成
        workflow.status = 'completed'
        workflow.actual_end_date = datetime.utcnow().date()

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '流程已推进',
        'data': workflow.to_dict()
    })


@service_workflow_bp.route('/<int:id>/pause', methods=['POST'])
@jwt_required_v2
def pause_workflow(current_user, id):
    """暂停流程"""
    workflow = CustomerWorkflow.query.get_or_404(id)
    workflow.status = 'paused'
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '流程已暂停',
        'data': workflow.to_dict()
    })


@service_workflow_bp.route('/<int:id>/resume', methods=['POST'])
@jwt_required_v2
def resume_workflow(current_user, id):
    """恢复流程"""
    workflow = CustomerWorkflow.query.get_or_404(id)
    workflow.status = 'active'
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '流程已恢复',
        'data': workflow.to_dict()
    })


# ========== 节点记录管理 ==========

@service_workflow_bp.route('/<int:workflow_id>/records', methods=['GET'])
@jwt_required_v2
def get_node_records(current_user, workflow_id):
    """获取节点记录列表"""
    records = WorkflowNodeRecord.query.filter_by(
        workflow_id=workflow_id
    ).order_by(WorkflowNodeRecord.created_at.desc()).all()

    return jsonify({
        'code': 200,
        'data': [r.to_dict() for r in records]
    })


@service_workflow_bp.route('/records/<int:record_id>', methods=['PUT'])
@jwt_required_v2
def update_node_record(current_user, record_id):
    """更新节点记录（汇报/提交）"""
    record = WorkflowNodeRecord.query.get_or_404(record_id)
    data = request.get_json()

    if 'status' in data:
        record.status = data['status']
        if data['status'] == 'processing' and not record.started_at:
            record.started_at = datetime.utcnow()
        if data['status'] == 'completed':
            record.completed_at = datetime.utcnow()
            record.executed_by = current_user.get('id')

    if 'content' in data:
        record.content = data['content']
    if 'attachments' in data:
        record.attachments = data['attachments']
    if 'related_data' in data:
        record.related_data = data['related_data']
    if 'remark' in data:
        record.remark = data['remark']
    if 'assigned_to' in data:
        record.assigned_to = data['assigned_to']
        record.assigned_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': record.to_dict()
    })


@service_workflow_bp.route('/records/<int:record_id>/assign', methods=['POST'])
@jwt_required_v2
def assign_node(current_user, record_id):
    """指派节点负责人"""
    record = WorkflowNodeRecord.query.get_or_404(record_id)
    data = request.get_json()

    record.assigned_to = data['employee_id']
    record.assigned_at = datetime.utcnow()
    record.deadline = data.get('deadline')

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '指派成功',
        'data': record.to_dict()
    })


# ========== 我的工作台 ==========

@service_workflow_bp.route('/my-tasks', methods=['GET'])
@jwt_required_v2
def get_my_tasks(current_user):
    """获取我的任务"""
    employee_id = current_user.get('id')
    status = request.args.get('status', 'pending')

    query = WorkflowNodeRecord.query.filter_by(assigned_to=employee_id)

    if status == 'pending':
        query = query.filter(WorkflowNodeRecord.status.in_(['pending', 'processing']))
    elif status == 'completed':
        query = query.filter_by(status='completed')

    records = query.order_by(WorkflowNodeRecord.deadline.asc()).all()

    return jsonify({
        'code': 200,
        'data': [r.to_dict() for r in records]
    })


@service_workflow_bp.route('/my-stats', methods=['GET'])
@jwt_required_v2
def get_my_stats(current_user):
    """获取我的工作统计"""
    employee_id = current_user.get('id')

    # 待处理任务
    pending_count = WorkflowNodeRecord.query.filter_by(
        assigned_to=employee_id,
        status='pending'
    ).count()

    # 进行中任务
    processing_count = WorkflowNodeRecord.query.filter_by(
        assigned_to=employee_id,
        status='processing'
    ).count()

    # 本月已完成
    from datetime import date
    start_of_month = date.today().replace(day=1)
    completed_this_month = WorkflowNodeRecord.query.filter(
        WorkflowNodeRecord.assigned_to == employee_id,
        WorkflowNodeRecord.status == 'completed',
        WorkflowNodeRecord.completed_at >= start_of_month
    ).count()

    # 即将到期（3天内）
    from datetime import timedelta
    deadline_soon = WorkflowNodeRecord.query.filter(
        WorkflowNodeRecord.assigned_to == employee_id,
        WorkflowNodeRecord.status.in_(['pending', 'processing']),
        WorkflowNodeRecord.deadline <= datetime.utcnow() + timedelta(days=3)
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'pending': pending_count,
            'processing': processing_count,
            'completed_this_month': completed_this_month,
            'deadline_soon': deadline_soon
        }
    })


# ========== 统计报表 ==========

@service_workflow_bp.route('/statistics', methods=['GET'])
@jwt_required_v2
def get_statistics(current_user):
    """获取流程统计"""
    # 各阶段流程数量
    phase_stats = db.session.query(
        CustomerWorkflow.current_phase,
        db.func.count(CustomerWorkflow.id)
    ).filter_by(is_deleted=False).group_by(CustomerWorkflow.current_phase).all()

    # 状态统计
    status_stats = db.session.query(
        CustomerWorkflow.status,
        db.func.count(CustomerWorkflow.id)
    ).filter_by(is_deleted=False).group_by(CustomerWorkflow.status).all()

    # 本月新增
    from datetime import date
    start_of_month = date.today().replace(day=1)
    new_this_month = CustomerWorkflow.query.filter(
        CustomerWorkflow.created_at >= start_of_month,
        CustomerWorkflow.is_deleted == False
    ).count()

    # 本月完工
    completed_this_month = CustomerWorkflow.query.filter(
        CustomerWorkflow.actual_end_date >= start_of_month,
        CustomerWorkflow.is_deleted == False
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'by_phase': {p: c for p, c in phase_stats},
            'by_status': {s: c for s, c in status_stats},
            'new_this_month': new_this_month,
            'completed_this_month': completed_this_month
        }
    })
