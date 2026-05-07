"""
物料管理模块 - API路由
V3.0 全新设计
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.material_sku import (
    MaterialSKU, MaterialCategory, MaterialVariant, MaterialSupplier,
    CALC_TYPES, CUSTOMIZATION_RULE_TYPES, SKU_STATUS
)
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime

material_sku_bp = Blueprint('material_sku', __name__, url_prefix='/api/v3/materials')


# ========== 分类管理 ==========

@material_sku_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取分类树（公开接口）"""
    from sqlalchemy import or_ as sql_or
    # 支持 is_deleted=False 和 is_deleted=NULL 两种情况（迁移数据可能为NULL）
    categories = MaterialCategory.query.filter(
        MaterialCategory.parent_id == None,
        sql_or(MaterialCategory.is_deleted == False, MaterialCategory.is_deleted.is_(None)),
        MaterialCategory.is_enabled == True
    ).order_by(MaterialCategory.sort_order).all()
    return jsonify({
        'code': 200,
        'data': [c.to_dict() for c in categories]
    })


@material_sku_bp.route('/categories', methods=['POST'])
@jwt_required_v2
def create_category(current_user):
    """创建分类"""
    data = request.get_json()

    category = MaterialCategory(
        name=data['name'],
        code=data.get('code'),
        parent_id=data.get('parent_id'),
        level=data.get('level', 1),
        icon=data.get('icon'),
        color=data.get('color', '#8B5A2B'),
        sort_order=data.get('sort_order', 0)
    )

    db.session.add(category)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': category.to_dict()
    })


@material_sku_bp.route('/categories/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_category(current_user, id):
    """更新分类"""
    category = MaterialCategory.query.get_or_404(id)
    data = request.get_json()

    category.name = data.get('name', category.name)
    category.code = data.get('code', category.code)
    category.icon = data.get('icon', category.icon)
    category.color = data.get('color', category.color)
    category.sort_order = data.get('sort_order', category.sort_order)
    category.is_enabled = data.get('is_enabled', category.is_enabled)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': category.to_dict()
    })


@material_sku_bp.route('/categories/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_category(current_user, id):
    """删除分类"""
    category = MaterialCategory.query.get_or_404(id)

    # 检查是否有子分类
    if category.children:
        return jsonify({'code': 400, 'message': '请先删除子分类'}), 400

    # 检查是否有物料
    if category.materials.count() > 0:
        return jsonify({'code': 400, 'message': '该分类下还有物料，无法删除'}), 400

    category.is_deleted = True
    db.session.commit()

    return jsonify({'code': 200, 'message': '删除成功'})


# ========== 物料管理 ==========

@material_sku_bp.route('', methods=['GET'])
def get_materials():
    """获取物料列表（公开接口）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', '')
    # 支持逗号分隔的多个 category_id（一级分类搜索其下所有二级分类）
    category_ids_raw = request.args.get('category_ids', '')
    status = request.args.get('status', 'active').strip()
    low_stock = request.args.get('low_stock', type=bool)

    query = MaterialSKU.query.filter_by(is_deleted=False)

    if status:
        query = query.filter_by(status=status)

    if keyword:
        query = query.filter(
            db.or_(
                MaterialSKU.name.contains(keyword),
                MaterialSKU.sku_code.contains(keyword),
                MaterialSKU.brand.contains(keyword)
            )
        )

    if category_id:
        try:
            cid = int(category_id)
            query = query.filter_by(category_id=cid)
        except ValueError:
            pass

    if category_ids_raw:
        # 支持逗号分隔的多个ID，用于一级分类搜索其下所有二级分类的物料
        try:
            cids = [int(x.strip()) for x in category_ids_raw.split(',') if x.strip()]
            if cids:
                query = query.filter(MaterialSKU.category_id.in_(cids))
        except ValueError:
            pass

    if low_stock:
        query = query.filter(MaterialSKU.stock_quantity <= MaterialSKU.stock_warning)

    query = query.order_by(MaterialSKU.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [m.to_dict() for m in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@material_sku_bp.route('/<int:id>', methods=['GET'])
def get_material(id):
    """获取物料详情（公开接口）"""
    material = MaterialSKU.query.get_or_404(id)
    return jsonify({
        'code': 200,
        'data': material.to_dict(include_variants=True)
    })


@material_sku_bp.route('', methods=['POST'])
@jwt_required_v2
def create_material(current_user):
    """创建物料"""
    data = request.get_json()

    # 生成SKU编码
    sku_code = data.get('sku_code') or generate_sku_code()

    material = MaterialSKU(
        sku_code=sku_code,
        name=data['name'],
        category_id=data.get('category_id'),
        brand=data.get('brand'),
        model=data.get('model'),
        specification=data.get('specification'),
        material=data.get('material'),
        origin=data.get('origin'),
        main_image=data.get('main_image'),
        images=data.get('images', []),
        cost_price=data.get('cost_price', 0),
        sale_price=data.get('sale_price', 0),
        market_price=data.get('market_price'),
        unit=data.get('unit', '件'),
        calc_type=data.get('calc_type', 'quantity'),
        stock_quantity=data.get('stock_quantity', 0),
        stock_warning=data.get('stock_warning', 10),
        customization_rules=data.get('customization_rules', []),
        has_variants=data.get('has_variants', False),
        variant_options=data.get('variant_options', []),
        has_craft_parts=data.get('has_craft_parts', False),
        craft_parts=data.get('craft_parts', []),
        description=data.get('description'),
        tags=data.get('tags', []),
        status=data.get('status', 'active'),
        created_by=1
    )

    db.session.add(material)
    db.session.flush()

    # 创建变体
    if data.get('variants'):
        for v_data in data['variants']:
            variant = MaterialVariant(
                sku_id=material.id,
                variant_code=v_data.get('variant_code'),
                variant_name=v_data.get('variant_name'),
                variant_values=v_data.get('variant_values'),
                image=v_data.get('image'),
                price_adjustment=v_data.get('price_adjustment', 0),
                stock_quantity=v_data.get('stock_quantity', 0)
            )
            db.session.add(variant)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': material.to_dict(include_variants=True)
    })


@material_sku_bp.route('/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_material(current_user, id):
    """更新物料"""
    material = MaterialSKU.query.get_or_404(id)
    data = request.get_json()

    # 更新基础字段
    fields = [
        'name', 'category_id', 'brand', 'model', 'specification',
        'material', 'origin', 'main_image', 'images', 'cost_price',
        'sale_price', 'market_price', 'unit', 'calc_type',
        'stock_quantity', 'stock_warning', 'customization_rules',
        'has_variants', 'variant_options', 'has_craft_parts',
        'craft_parts', 'description', 'tags', 'status'
    ]

    for field in fields:
        if field in data:
            setattr(material, field, data[field])

    # 更新变体
    if 'variants' in data:
        # 删除旧变体
        MaterialVariant.query.filter_by(sku_id=id).delete()
        # 创建新变体
        for v_data in data['variants']:
            variant = MaterialVariant(
                sku_id=material.id,
                variant_code=v_data.get('variant_code'),
                variant_name=v_data.get('variant_name'),
                variant_values=v_data.get('variant_values'),
                image=v_data.get('image'),
                price_adjustment=v_data.get('price_adjustment', 0),
                stock_quantity=v_data.get('stock_quantity', 0)
            )
            db.session.add(variant)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': material.to_dict(include_variants=True)
    })


@material_sku_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_material(current_user, id):
    """删除物料"""
    material = MaterialSKU.query.get_or_404(id)
    material.is_deleted = True
    db.session.commit()

    return jsonify({'code': 200, 'message': '删除成功'})


# ========== 变体管理 ==========

@material_sku_bp.route('/<int:sku_id>/variants', methods=['POST'])
@jwt_required_v2
def add_variant(current_user, sku_id):
    """添加变体"""
    data = request.get_json()

    variant = MaterialVariant(
        sku_id=sku_id,
        variant_code=data.get('variant_code'),
        variant_name=data.get('variant_name'),
        variant_values=data.get('variant_values'),
        image=data.get('image'),
        price_adjustment=data.get('price_adjustment', 0),
        stock_quantity=data.get('stock_quantity', 0)
    )

    db.session.add(variant)

    # 更新SKU的变体状态
    sku = MaterialSKU.query.get(sku_id)
    sku.has_variants = True

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': variant.to_dict()
    })


@material_sku_bp.route('/variants/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_variant(current_user, id):
    """更新变体"""
    variant = MaterialVariant.query.get_or_404(id)
    data = request.get_json()

    variant.variant_code = data.get('variant_code', variant.variant_code)
    variant.variant_name = data.get('variant_name', variant.variant_name)
    variant.variant_values = data.get('variant_values', variant.variant_values)
    variant.image = data.get('image', variant.image)
    variant.price_adjustment = data.get('price_adjustment', variant.price_adjustment)
    variant.stock_quantity = data.get('stock_quantity', variant.stock_quantity)
    variant.is_enabled = data.get('is_enabled', variant.is_enabled)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': variant.to_dict()
    })


@material_sku_bp.route('/variants/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_variant(current_user, id):
    """删除变体"""
    variant = MaterialVariant.query.get_or_404(id)
    db.session.delete(variant)
    db.session.commit()

    return jsonify({'code': 200, 'message': '删除成功'})


# ========== 供应商管理 ==========

@material_sku_bp.route('/suppliers', methods=['GET'])
@jwt_required_v2
def get_suppliers(current_user):
    """获取供应商列表"""
    keyword = request.args.get('keyword', '').strip()
    status = request.args.get('status', '').strip()
    
    query = MaterialSupplier.query.filter_by(is_deleted=False)
    
    if keyword:
        query = query.filter(
            db.or_(
                MaterialSupplier.name.contains(keyword),
                MaterialSupplier.contact_person.contains(keyword),
                MaterialSupplier.phone.contains(keyword)
            )
        )
    
    if status:
        query = query.filter_by(status=status)
    
    suppliers = query.order_by(MaterialSupplier.created_at.desc()).all()
    return jsonify({
        'code': 200,
        'data': [s.to_dict() for s in suppliers]
    })


@material_sku_bp.route('/suppliers/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_supplier(current_user, id):
    """更新供应商"""
    supplier = MaterialSupplier.query.get_or_404(id)
    data = request.get_json()
    
    supplier.name = data.get('name', supplier.name)
    supplier.contact_person = data.get('contact_person', supplier.contact_person)
    supplier.phone = data.get('phone', supplier.phone)
    supplier.email = data.get('email', supplier.email)
    supplier.address = data.get('address', supplier.address)
    supplier.status = data.get('status', supplier.status)
    supplier.remark = data.get('remark', supplier.remark)
    
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': supplier.to_dict()
    })


@material_sku_bp.route('/suppliers/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_supplier(current_user, id):
    """删除供应商"""
    supplier = MaterialSupplier.query.get_or_404(id)
    supplier.is_deleted = True
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'})


@material_sku_bp.route('/suppliers', methods=['POST'])
@jwt_required_v2
def create_supplier(current_user):
    """创建供应商"""
    data = request.get_json()

    supplier = MaterialSupplier(
        name=data['name'],
        contact_person=data.get('contact_person'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        remark=data.get('remark')
    )

    db.session.add(supplier)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': supplier.to_dict()
    })


# ========== 选项字典 ==========

@material_sku_bp.route('/options', methods=['GET'])
@jwt_required_v2
def get_options(current_user):
    """获取选项字典"""
    return jsonify({
        'code': 200,
        'data': {
            'calc_types': CALC_TYPES,
            'customization_rule_types': CUSTOMIZATION_RULE_TYPES,
            'sku_status': SKU_STATUS
        }
    })


# ========== 分类统计 ==========

@material_sku_bp.route('/category-stats', methods=['GET'])
@jwt_required_v2
def get_category_stats(current_user):
    """获取分类物料统计"""
    # 获取所有分类
    categories = MaterialCategory.query.filter_by(is_deleted=False).all()
    
    stats = {}
    for cat in categories:
        # 获取该分类及其子分类的所有物料
        cat_ids = [cat.id] + [c.id for c in cat.children if not c.is_deleted]
        
        total = MaterialSKU.query.filter(
            MaterialSKU.category_id.in_(cat_ids),
            MaterialSKU.is_deleted == False
        ).count()
        
        active = MaterialSKU.query.filter(
            MaterialSKU.category_id.in_(cat_ids),
            MaterialSKU.is_deleted == False,
            MaterialSKU.status == 'active'
        ).count()
        
        low_stock = MaterialSKU.query.filter(
            MaterialSKU.category_id.in_(cat_ids),
            MaterialSKU.is_deleted == False,
            MaterialSKU.stock_quantity <= MaterialSKU.stock_warning
        ).count()
        
        stats[cat.id] = {
            'total': total,
            'active': active,
            'low_stock': low_stock
        }
    
    return jsonify({'code': 200, 'data': stats})


# ========== 供应商统计 ==========

@material_sku_bp.route('/supplier-stats', methods=['GET'])
@jwt_required_v2
def get_supplier_stats(current_user):
    """获取供应商统计"""
    total = MaterialSupplier.query.filter_by(is_deleted=False).count()
    
    status_stats = db.session.query(
        MaterialSupplier.status,
        db.func.count(MaterialSupplier.id)
    ).filter_by(is_deleted=False).group_by(MaterialSupplier.status).all()
    
    return jsonify({
        'code': 200,
        'data': {
            'total': total,
            'active': dict(status_stats).get('active', 0),
            'paused': dict(status_stats).get('paused', 0),
            'terminated': dict(status_stats).get('terminated', 0),
            'material_count': MaterialSKU.query.filter_by(is_deleted=False).count()
        }
    })


# ========== 统计 ==========

@material_sku_bp.route('/stats', methods=['GET'])
@jwt_required_v2
def get_stats(current_user):
    """获取物料统计"""
    # 总物料数
    total = MaterialSKU.query.filter_by(is_deleted=False).count()

    # 按状态统计
    status_stats = db.session.query(
        MaterialSKU.status,
        db.func.count(MaterialSKU.id)
    ).filter_by(is_deleted=False).group_by(MaterialSKU.status).all()

    # 低库存物料
    low_stock = MaterialSKU.query.filter(
        MaterialSKU.is_deleted == False,
        MaterialSKU.stock_quantity <= MaterialSKU.stock_warning
    ).count()

    # 按分类统计
    category_stats = db.session.query(
        MaterialCategory.name,
        db.func.count(MaterialSKU.id)
    ).join(MaterialSKU, MaterialCategory.id == MaterialSKU.category_id).filter(
        MaterialSKU.is_deleted == False
    ).group_by(MaterialCategory.name).all()

    # 计算今日新增（过去24小时）
    from datetime import datetime, timedelta
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = MaterialSKU.query.filter(
        MaterialSKU.is_deleted == False,
        MaterialSKU.created_at >= today_start
    ).count()

    # 在售物料（active 状态）
    active_count = dict(status_stats).get('active', 0)

    return jsonify({
        'code': 200,
        'data': {
            'total': total,
            'active': active_count,
            'warning': low_stock,
            'today': today_count
        }
    })


# ========== 品牌列表 ==========

@material_sku_bp.route('/brands', methods=['GET'])
@jwt_required_v2
def get_brands(current_user):
    """获取品牌列表（从物料中提取）"""
    from sqlalchemy import distinct
    brands = db.session.query(distinct(MaterialSKU.brand)).filter(
        MaterialSKU.brand.isnot(None),
        MaterialSKU.brand != '',
        MaterialSKU.is_deleted == False
    ).order_by(MaterialSKU.brand).all()
    
    return jsonify({
        'code': 200,
        'data': [b[0] for b in brands if b[0]]
    })


# ========== 辅助函数 ==========

def generate_sku_code():
    """生成SKU编码"""
    import random
    import string
    prefix = 'SKU'
    suffix = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{suffix}"


# ========== Public Display Config ==========

@material_sku_bp.route('/public-config', methods=['GET'])
@jwt_required_v2
def get_public_config(current_user):
    """Get public display config for frontend"""
    # Get categories with public materials
    public_categories = db.session.query(
        MaterialSKU.category_id
    ).filter(
        MaterialSKU.is_deleted == False,
        MaterialSKU.is_public == True,
        MaterialSKU.category_id.isnot(None)
    ).distinct().all()
    
    # Get brands with public materials
    public_brands = db.session.query(
        MaterialSKU.brand
    ).filter(
        MaterialSKU.is_deleted == False,
        MaterialSKU.is_public == True,
        MaterialSKU.brand.isnot(None),
        MaterialSKU.brand != ''
    ).distinct().all()
    
    # Count total public materials
    total_public = MaterialSKU.query.filter(
        MaterialSKU.is_deleted == False,
        MaterialSKU.is_public == True
    ).count()
    
    return jsonify({
        'code': 200,
        'data': {
            'categories': [c[0] for c in public_categories if c[0]],
            'brands': [b[0] for b in public_brands if b[0]],
            'total': total_public
        }
    })


@material_sku_bp.route('/public-config', methods=['POST'])
@jwt_required_v2
def save_public_config(current_user):
    """Save public display config - batch update is_public field"""
    from sqlalchemy import or_
    
    data = request.get_json() or {}
    categories = data.get('categories', [])
    brands = data.get('brands', [])
    
    # First, set all materials to not public
    MaterialSKU.query.update({'is_public': False})
    
    # Then, set selected categories and brands to public
    if categories or brands:
        query = MaterialSKU.query.filter(MaterialSKU.is_deleted == False)
        
        conditions = []
        if categories:
            conditions.append(MaterialSKU.category_id.in_(categories))
        if brands:
            conditions.append(MaterialSKU.brand.in_(brands))
        
        if conditions:
            query.filter(or_(*conditions)).update({'is_public': True}, synchronize_session=False)
    
    db.session.commit()
    
    # Return updated stats
    total_public = MaterialSKU.query.filter(
        MaterialSKU.is_deleted == False,
        MaterialSKU.is_public == True
    ).count()
    
    return jsonify({
        'code': 200,
        'message': 'Saved successfully',
        'data': {
            'total': total_public
        }
    })
