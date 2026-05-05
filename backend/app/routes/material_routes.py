"""
物料管理模块路由 - 完整CRUD
API端点: /api/v3/materials
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models.material_sku import MaterialSKU, MaterialCategory
from sqlalchemy import text, or_

material_bp = Blueprint('material', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


# ========== 物料CRUD ==========

@material_bp.route('/materials', methods=['GET'])
def get_materials():
    """获取物料列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', type=int)
    is_public = request.args.get('is_public', type=int)
    
    query = MaterialSKU.query.filter_by(is_deleted=False)
    
    if keyword:
        query = query.filter(
            db.or_(
                MaterialSKU.name.contains(keyword),
                MaterialSKU.sku_code.contains(keyword),
                MaterialSKU.brand.contains(keyword)
            )
        )
    
    if category_id:
        # 包括子分类
        cat = MaterialCategory.query.get(category_id)
        if cat and cat.level == 1:
            sub_ids = [c.id for c in cat.children] + [category_id]
            query = query.filter(MaterialSKU.category_id.in_(sub_ids))
        else:
            query = query.filter_by(category_id=category_id)
    
    if is_public is not None:
        query = query.filter_by(is_public=(is_public == 1))
    
    query = query.order_by(MaterialSKU.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    return api_response(data={
        'items': [m.to_dict(include_variants=True) for m in pagination.items],
        'total': pagination.total,
        'page': page,
        'page_size': page_size
    })


@material_bp.route('/materials', methods=['POST'])
def create_material():
    """创建物料"""
    data = request.get_json()
    if not data:
        return api_response(code=400, message='无效的请求数据')
    
    try:
        sku = MaterialSKU(
            sku_code=data.get('sku_code'),
            name=data.get('name'),
            category_id=data.get('category_id'),
            brand=data.get('brand'),
            model=data.get('model'),
            specification=data.get('specification'),
            material=data.get('material'),
            origin=data.get('origin'),
            main_image=data.get('main_image'),
            cost_price=data.get('cost_price', 0),
            sale_price=data.get('sale_price', 0),
            market_price=data.get('market_price'),
            unit=data.get('unit', '件'),
            calc_type=data.get('calc_type', 'quantity'),
            stock_quantity=data.get('stock_quantity', 0),
            stock_warning=data.get('stock_warning', 10),
            has_variants=data.get('has_variants', False),
            variant_options=data.get('variant_options', []),
            has_craft_parts=data.get('has_craft_parts', False),
            craft_parts=data.get('craft_parts', []),
            description=data.get('description'),
            detail_content=data.get('detail_content'),
            tags=data.get('tags', []),
            status=data.get('status', 'active'),
            is_public=data.get('is_public', True),
            created_by=data.get('created_by')
        )
        db.session.add(sku)
        db.session.commit()
        
        return api_response(code=200, message='创建成功', data=sku.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'创建失败: {str(e)}')


@material_bp.route('/materials/<int:sku_id>', methods=['GET'])
def get_material(sku_id):
    """获取单个物料详情"""
    sku = MaterialSKU.query.get_or_404(sku_id)
    if sku.is_deleted:
        return api_response(code=404, message='物料不存在')
    return api_response(data=sku.to_dict(include_variants=True))


@material_bp.route('/materials/<int:sku_id>', methods=['PUT'])
def update_material(sku_id):
    """更新物料"""
    sku = MaterialSKU.query.get_or_404(sku_id)
    if sku.is_deleted:
        return api_response(code=404, message='物料不存在')
    
    data = request.get_json()
    if not data:
        return api_response(code=400, message='无效的请求数据')
    
    try:
        sku.name = data.get('name', sku.name)
        sku.category_id = data.get('category_id', sku.category_id)
        sku.brand = data.get('brand', sku.brand)
        sku.model = data.get('model', sku.model)
        sku.specification = data.get('specification', sku.specification)
        sku.material = data.get('material', sku.material)
        sku.origin = data.get('origin', sku.origin)
        sku.main_image = data.get('main_image', sku.main_image)
        sku.cost_price = data.get('cost_price', sku.cost_price)
        sku.sale_price = data.get('sale_price', sku.sale_price)
        sku.market_price = data.get('market_price', sku.market_price)
        sku.unit = data.get('unit', sku.unit)
        sku.calc_type = data.get('calc_type', sku.calc_type)
        sku.stock_quantity = data.get('stock_quantity', sku.stock_quantity)
        sku.stock_warning = data.get('stock_warning', sku.stock_warning)
        sku.has_variants = data.get('has_variants', sku.has_variants)
        sku.variant_options = data.get('variant_options', sku.variant_options)
        sku.has_craft_parts = data.get('has_craft_parts', sku.has_craft_parts)
        sku.craft_parts = data.get('craft_parts', sku.craft_parts)
        sku.description = data.get('description', sku.description)
        sku.detail_content = data.get('detail_content', sku.detail_content)
        sku.tags = data.get('tags', sku.tags)
        sku.status = data.get('status', sku.status)
        sku.is_public = data.get('is_public', sku.is_public)
        sku.updated_at = datetime.utcnow()
        
        db.session.commit()
        return api_response(message='更新成功', data=sku.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'更新失败: {str(e)}')


@material_bp.route('/materials/<int:sku_id>', methods=['DELETE'])
def delete_material(sku_id):
    """删除物料（软删除）"""
    sku = MaterialSKU.query.get_or_404(sku_id)
    if sku.is_deleted:
        return api_response(code=404, message='物料不存在')
    
    try:
        sku.is_deleted = True
        sku.updated_at = datetime.utcnow()
        db.session.commit()
        return api_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'删除失败: {str(e)}')


# ========== 分类管理 ==========

@material_bp.route('/materials/categories', methods=['GET'])
def get_categories():
    """获取分类树"""
    from sqlalchemy import or_
    categories = MaterialCategory.query.filter(
        MaterialCategory.level == 1,
        or_(MaterialCategory.is_deleted == False, MaterialCategory.is_deleted.is_(None))
    ).order_by(MaterialCategory.sort_order).all()
    return api_response(data=[c.to_dict() for c in categories])


@material_bp.route('/materials/categories', methods=['POST'])
def create_category():
    """创建分类"""
    data = request.get_json()
    if not data or 'name' not in data:
        return api_response(code=400, message='分类名称不能为空')
    
    try:
        category = MaterialCategory(
            name=data['name'],
            code=data.get('code'),
            parent_id=data.get('parent_id'),
            level=data.get('level', 1),
            icon=data.get('icon'),
            color=data.get('color', '#8B5A2B'),
            sort_order=data.get('sort_order', 0),
            is_enabled=data.get('is_enabled', True)
        )
        db.session.add(category)
        db.session.commit()
        return api_response(code=200, message='分类创建成功', data=category.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'分类创建失败: {str(e)}')


@material_bp.route('/materials/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    """更新分类"""
    category = MaterialCategory.query.get_or_404(cat_id)
    if category.is_deleted:
        return api_response(code=404, message='分类不存在')
    
    data = request.get_json()
    if not data:
        return api_response(code=400, message='无效的请求数据')
    
    try:
        category.name = data.get('name', category.name)
        category.code = data.get('code', category.code)
        category.icon = data.get('icon', category.icon)
        category.color = data.get('color', category.color)
        category.sort_order = data.get('sort_order', category.sort_order)
        category.is_enabled = data.get('is_enabled', category.is_enabled)
        category.updated_at = datetime.utcnow()
        
        db.session.commit()
        return api_response(message='分类更新成功', data=category.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'分类更新失败: {str(e)}')


@material_bp.route('/materials/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    """删除分类（软删除）"""
    category = MaterialCategory.query.get_or_404(cat_id)
    if category.is_deleted:
        return api_response(code=404, message='分类不存在')
    
    try:
        # 检查是否有子分类
        if category.children:
            return api_response(code=400, message='请先删除子分类')
        
        # 检查是否有关联物料
        if category.materials.filter_by(is_deleted=False).count() > 0:
            return api_response(code=400, message='该分类下有关联物料，无法删除')
        
        category.is_deleted = True
        category.updated_at = datetime.utcnow()
        db.session.commit()
        return api_response(message='分类删除成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'分类删除失败: {str(e)}')


# ========== 花色管理（material_color表） ==========

@material_bp.route('/materials/<int:sku_id>/colors', methods=['GET'])
def get_material_colors(sku_id):
    """获取物料的花色列表"""
    sku = MaterialSKU.query.get_or_404(sku_id)
    if sku.is_deleted:
        return api_response(code=404, message='物料不存在')
    
    conn = db.engine.connect()
    result = conn.execute(text("""
        SELECT id, color_name, color_code, image, stock_quantity, price_adjustment, is_enabled
        FROM material_color
        WHERE sku_id = :sku_id AND is_enabled = 1
        ORDER BY id
    """), {'sku_id': sku_id})
    
    colors = []
    for row in result.fetchall():
        colors.append({
            'id': row[0],
            'color_name': row[1],
            'color_code': row[2],
            'image': row[3],
            'stock_quantity': row[4],
            'price_adjustment': float(row[5]) if row[5] else 0,
            'is_enabled': row[6]
        })
    
    return api_response(data=colors)


@material_bp.route('/materials/<int:sku_id>/colors', methods=['POST'])
def add_material_color(sku_id):
    """添加花色"""
    sku = MaterialSKU.query.get_or_404(sku_id)
    if sku.is_deleted:
        return api_response(code=404, message='物料不存在')
    
    data = request.get_json()
    if not data or 'color_name' not in data:
        return api_response(code=400, message='花色名称不能为空')
    
    try:
        conn = db.engine.connect()
        conn.execute(text("""
            INSERT INTO material_color (sku_id, color_name, color_code, image, stock_quantity, price_adjustment, is_enabled, created_at, updated_at)
            VALUES (:sku_id, :color_name, :color_code, :image, :stock_quantity, :price_adjustment, 1, :now, :now)
        """), {
            'sku_id': sku_id,
            'color_name': data['color_name'],
            'color_code': data.get('color_code'),
            'image': data.get('image'),
            'stock_quantity': data.get('stock_quantity', 0),
            'price_adjustment': data.get('price_adjustment', 0),
            'now': datetime.utcnow()
        })
        conn.commit()
        
        return api_response(code=200, message='花色添加成功')
    except Exception as e:
        return api_response(code=500, message=f'花色添加失败: {str(e)}')


@material_bp.route('/materials/colors/<int:color_id>', methods=['PUT'])
def update_material_color(color_id):
    """更新花色"""
    conn = db.engine.connect()
    data = request.get_json()
    if not data:
        return api_response(code=400, message='无效的请求数据')
    
    try:
        conn.execute(text("""
            UPDATE material_color
            SET color_name = :color_name, color_code = :color_code, image = :image,
                stock_quantity = :stock_quantity, price_adjustment = :price_adjustment,
                updated_at = :now
            WHERE id = :color_id
        """), {
            'color_id': color_id,
            'color_name': data.get('color_name'),
            'color_code': data.get('color_code'),
            'image': data.get('image'),
            'stock_quantity': data.get('stock_quantity'),
            'price_adjustment': data.get('price_adjustment'),
            'now': datetime.utcnow()
        })
        conn.commit()
        
        return api_response(message='花色更新成功')
    except Exception as e:
        return api_response(code=500, message=f'花色更新失败: {str(e)}')


@material_bp.route('/materials/colors/<int:color_id>', methods=['DELETE'])
def delete_material_color(color_id):
    """删除花色（软删除）"""
    try:
        conn = db.engine.connect()
        conn.execute(text("UPDATE material_color SET is_enabled = 0, updated_at = :now WHERE id = :color_id"), {
            'color_id': color_id,
            'now': datetime.utcnow()
        })
        conn.commit()
        
        return api_response(message='花色删除成功')
    except Exception as e:
        return api_response(code=500, message=f'花色删除失败: {str(e)}')


# ========== 公开API（前台展示） ==========

@material_bp.route('/materials/public', methods=['GET'])
def get_public_materials():
    """获取前台展示物料（按分类分组）"""
    categories = MaterialCategory.query.filter(
        MaterialCategory.level == 1,
        MaterialCategory.is_enabled == True,
        or_(MaterialCategory.is_deleted == False, MaterialCategory.is_deleted.is_(None))
    ).order_by(MaterialCategory.sort_order).all()
    
    result = []
    for cat in categories:
        # 获取该分类及其子分类下的所有公开物料（子分类也要处理 NULL is_deleted）
        sub_cats = MaterialCategory.query.filter(
            MaterialCategory.parent_id == cat.id,
            or_(MaterialCategory.is_deleted == False, MaterialCategory.is_deleted.is_(None))
        ).all()
        sub_cat_ids = [c.id for c in sub_cats] + [cat.id]
        materials = MaterialSKU.query.filter(
            MaterialSKU.category_id.in_(sub_cat_ids),
            MaterialSKU.is_deleted == False,
            MaterialSKU.is_public == True,
            MaterialSKU.status == 'active'
        ).limit(20).all()
        
        if materials:
            result.append({
                'category': cat.to_dict(),
                'materials': [m.to_dict() for m in materials]
            })
    
    return api_response(data=result)
