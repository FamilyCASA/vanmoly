"""
特殊工艺数据库 - API路由
独立于物料库，报价管理引用此库
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.craft_process import CraftProcess
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime

craft_bp = Blueprint('craft', __name__, url_prefix='/api/v3/crafts')


@craft_bp.route('', methods=['GET'])
@jwt_required_v2
def get_crafts(current_user):
    """获取工艺列表（分页+筛选）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category')
    is_enabled = request.args.get('is_enabled')

    query = CraftProcess.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_deleted=False
    )

    if keyword:
        query = query.filter(
            db.or_(
                CraftProcess.name.contains(keyword),
                CraftProcess.code.contains(keyword),
            )
        )
    if category:
        query = query.filter_by(category=category)
    if is_enabled is not None and is_enabled != '':
        query = query.filter_by(is_enabled=(is_enabled == 'true' or is_enabled == '1'))

    query = query.order_by(CraftProcess.sort_order, CraftProcess.created_at.desc())
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


@craft_bp.route('/all', methods=['GET'])
@jwt_required_v2
def get_all_crafts(current_user):
    """获取所有启用的工艺（不分页，用于下拉选择）"""
    category = request.args.get('category')

    query = CraftProcess.query.filter_by(
        tenant_id=current_user.get('tenant_id', '0'),
        is_deleted=False,
        is_enabled=True
    )

    if category:
        query = query.filter_by(category=category)

    crafts = query.order_by(CraftProcess.sort_order, CraftProcess.name).all()

    return jsonify({
        'code': 200,
        'data': [c.to_dict() for c in crafts]
    })


@craft_bp.route('/<int:id>', methods=['GET'])
@jwt_required_v2
def get_craft(current_user, id):
    """获取工艺详情"""
    craft = CraftProcess.query.get_or_404(id)
    return jsonify({
        'code': 200,
        'data': craft.to_dict()
    })


@craft_bp.route('', methods=['POST'])
@jwt_required_v2
def create_craft(current_user):
    """创建工艺"""
    data = request.get_json()

    if not data.get('name'):
        return jsonify({'code': 400, 'message': '工艺名称不能为空'}), 400
    if not data.get('category'):
        return jsonify({'code': 400, 'message': '工艺分类不能为空'}), 400

    craft = CraftProcess(
        tenant_id=current_user.get('tenant_id', '0'),
        name=data['name'],
        category=data['category'],
        code=data.get('code'),
        coefficient=data.get('coefficient', 1),
        unit_price=data.get('unit_price', 0),
        unit=data.get('unit', '项'),
        main_image=data.get('main_image'),
        construction_image=data.get('construction_image'),
        real_image=data.get('real_image'),
        description=data.get('description'),
        is_enabled=data.get('is_enabled', True),
        sort_order=data.get('sort_order', 0),
    )

    db.session.add(craft)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': craft.to_dict()
    })


@craft_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_craft(current_user, id):
    """更新工艺"""
    craft = CraftProcess.query.get_or_404(id)
    data = request.get_json()

    if 'name' in data:
        craft.name = data['name']
    if 'category' in data:
        craft.category = data['category']
    if 'code' in data:
        craft.code = data['code']
    if 'coefficient' in data:
        craft.coefficient = data['coefficient']
    if 'unit_price' in data:
        craft.unit_price = data['unit_price']
    if 'unit' in data:
        craft.unit = data['unit']
    if 'main_image' in data:
        craft.main_image = data['main_image']
    if 'construction_image' in data:
        craft.construction_image = data['construction_image']
    if 'real_image' in data:
        craft.real_image = data['real_image']
    if 'description' in data:
        craft.description = data['description']
    if 'is_enabled' in data:
        craft.is_enabled = data['is_enabled']
    if 'sort_order' in data:
        craft.sort_order = data['sort_order']

    craft.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': craft.to_dict()
    })


@craft_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_craft(current_user, id):
    """删除工艺（软删除）"""
    craft = CraftProcess.query.get_or_404(id)
    craft.is_deleted = True
    craft.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@craft_bp.route('/batch-delete', methods=['POST'])
@jwt_required_v2
def batch_delete_crafts(current_user):
    """批量删除工艺"""
    data = request.get_json()
    ids = data.get('ids', [])

    if not ids:
        return jsonify({'code': 400, 'message': '请选择要删除的工艺'}), 400

    updated = CraftProcess.query.filter(
        CraftProcess.id.in_(ids),
        CraftProcess.tenant_id == current_user.get('tenant_id', '0'),
        CraftProcess.is_deleted == False
    ).update({'is_deleted': True, 'updated_at': datetime.utcnow()}, synchronize_session=False)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': f'成功删除 {updated} 条工艺'
    })


@craft_bp.route('/toggle-status', methods=['POST'])
@jwt_required_v2
def toggle_craft_status(current_user):
    """切换工艺启用/禁用状态"""
    data = request.get_json()
    craft_id = data.get('id')

    if not craft_id:
        return jsonify({'code': 400, 'message': '缺少工艺ID'}), 400

    craft = CraftProcess.query.get_or_404(craft_id)
    craft.is_enabled = not craft.is_enabled
    craft.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': f'已{"启用" if craft.is_enabled else "禁用"}',
        'data': craft.to_dict()
    })
