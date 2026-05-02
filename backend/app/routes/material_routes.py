"""
销售物料模块路由
API端点: /api/v3/materials
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models.material_sku import MaterialSKU, MaterialCategory


material_bp = Blueprint('material', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


@material_bp.route('/materials', methods=['GET'])
def get_materials():
    """获取销售物料列表 - 使用SKU数据"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', type=int)
    
    query = MaterialSKU.query.filter_by(is_deleted=False, status='active')
    
    if keyword:
        query = query.filter(
            db.or_(
                MaterialSKU.name.contains(keyword),
                MaterialSKU.sku_code.contains(keyword),
                MaterialSKU.brand.contains(keyword)
            )
        )
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    query = query.order_by(MaterialSKU.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    return api_response(data={
        'items': [m.to_dict() for m in pagination.items],
        'total': pagination.total,
        'page': page,
        'page_size': page_size
    })


@material_bp.route('/materials', methods=['POST'])
def create_material():
    """创建销售物料"""
    return api_response(code=404, message='功能开发中')
