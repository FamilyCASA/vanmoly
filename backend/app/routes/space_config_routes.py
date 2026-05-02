# -*- coding: utf-8 -*-
"""
空间配置模块 - API路由
V3.2 新增：案例空间配置模板管理
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.space_config import (
    CaseSpaceConfig, CaseSpaceConfigItem, 
    QuoteSpaceInstance, MaterialExclusiveRule
)
from app.models.case import CaseStudy
from app.models.material_sku import MaterialSKU
from app.routes.auth_routes_v2 import jwt_required_v2
from datetime import datetime
import json

space_config_bp = Blueprint('space_config', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


# ==================== 空间配置模板管理 ====================

@space_config_bp.route('', methods=['GET'])
@jwt_required_v2
def get_configs(current_user):
    """获取空间配置列表"""
    try:
        # 分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 筛选参数
        case_id = request.args.get('case_id', type=int)
        space_type = request.args.get('space_type')
        version_level = request.args.get('version_level')
        is_template = request.args.get('is_template', type=int)
        status = request.args.get('status', 'active')
        keyword = request.args.get('keyword', '').strip()
        
        # 构建查询
        query = CaseSpaceConfig.query.filter_by(
            tenant_id=current_user.get('tenant_id', '0'),
            status=status
        )
        
        if case_id:
            query = query.filter_by(case_id=case_id)
        if space_type:
            query = query.filter_by(space_type=space_type)
        if version_level:
            query = query.filter_by(version_level=version_level)
        if is_template is not None:
            query = query.filter_by(is_template=bool(is_template))
        if keyword:
            query = query.filter(
                db.or_(
                    CaseSpaceConfig.config_name.contains(keyword),
                    CaseSpaceConfig.space_name.contains(keyword)
                )
            )
        
        query = query.order_by(CaseSpaceConfig.updated_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        items = [item.to_dict() for item in pagination.items]
        
        return api_response(data={
            'items': items,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages
        })
        
    except Exception as e:
        return api_response(500, f'查询失败: {str(e)}')


@space_config_bp.route('/<int:config_id>', methods=['GET'])
@jwt_required_v2
def get_config(current_user, config_id):
    """获取空间配置详情"""
    try:
        config = CaseSpaceConfig.query.filter_by(
            id=config_id,
            tenant_id=current_user.get('tenant_id', '0')
        ).first()
        
        if not config:
            return api_response(404, '配置不存在')
        
        return api_response(data=config.to_dict(include_items=True))
        
    except Exception as e:
        return api_response(500, f'查询失败: {str(e)}')


@space_config_bp.route('', methods=['POST'])
@jwt_required_v2
def create_config(current_user):
    """创建空间配置"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        if not data.get('case_id'):
            return api_response(400, '缺少案例ID')
        if not data.get('space_type'):
            return api_response(400, '缺少空间类型')
        if not data.get('version_level'):
            return api_response(400, '缺少版本档位')
        
        # 检查案例是否存在
        case = CaseStudy.query.get(data['case_id'])
        if not case:
            return api_response(404, '案例不存在')
        
        # 创建配置
        config = CaseSpaceConfig(
            tenant_id=current_user.get('tenant_id', '0'),
            case_id=data['case_id'],
            space_type=data['space_type'],
            space_name=data.get('space_name', data['space_type']),
            space_area=data.get('space_area'),
            version_level=data['version_level'],
            version_code=CaseSpaceConfig.get_version_code(data['version_level']),
            config_name=data.get('config_name', f"{case.style or '现代'}-{data['space_type']}-{data['version_level']}版"),
            config_desc=data.get('config_desc'),
            is_template=data.get('is_template', True),
            template_tags=data.get('template_tags'),
            created_by=current_user.get('id')
        )
        
        db.session.add(config)
        db.session.flush()  # 获取ID
        
        # 添加物料明细
        materials = data.get('materials', [])
        total_price = 0
        
        for idx, m in enumerate(materials):
            sku_id = m.get('sku_id')
            if not sku_id:
                continue
                
            # 获取物料信息
            sku = MaterialSKU.query.get(sku_id)
            if not sku:
                continue
            
            quantity = float(m.get('quantity', 1))
            unit_price = float(m.get('unit_price') or sku.retail_price or 0)
            item_total = quantity * unit_price
            
            item = CaseSpaceConfigItem(
                config_id=config.id,
                sku_id=sku_id,
                sku_code=sku.sku_code,
                sku_name=sku.name,
                brand=sku.brand,
                specification=sku.specification,
                category=m.get('category') or sku.category,
                quantity=quantity,
                unit=m.get('unit') or sku.unit,
                unit_price=unit_price,
                total_price=item_total,
                is_exclusive=m.get('is_exclusive', False),
                exclusive_group=m.get('exclusive_group'),
                is_optional=m.get('is_optional', False),
                is_default=m.get('is_default', True),
                sort_order=idx
            )
            
            db.session.add(item)
            total_price += item_total
        
        # 更新价格
        config.material_cost = total_price
        config.labor_cost = data.get('labor_cost', 0)
        config.design_cost = data.get('design_cost', 0)
        config.manage_cost = data.get('manage_cost', 0)
        config.total_price = total_price + float(config.labor_cost or 0) + float(config.design_cost or 0) + float(config.manage_cost or 0)
        config.material_count = len(materials)
        
        # 保存物料JSON快照
        config.materials = json.dumps([item.to_dict() for item in config.items])
        
        db.session.commit()
        
        return api_response(200, '创建成功', config.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return api_response(500, f'创建失败: {str(e)}')


@space_config_bp.route('/<int:config_id>', methods=['PUT'])
@jwt_required_v2
def update_config(current_user, config_id):
    """更新空间配置"""
    try:
        config = CaseSpaceConfig.query.filter_by(
            id=config_id,
            tenant_id=current_user.get('tenant_id', '0')
        ).first()
        
        if not config:
            return api_response(404, '配置不存在')
        
        data = request.get_json()
        
        # 更新基本信息
        config.space_name = data.get('space_name', config.space_name)
        config.space_area = data.get('space_area', config.space_area)
        config.config_name = data.get('config_name', config.config_name)
        config.config_desc = data.get('config_desc', config.config_desc)
        config.is_template = data.get('is_template', config.is_template)
        config.template_tags = data.get('template_tags', config.template_tags)
        
        # 更新价格
        if 'labor_cost' in data:
            config.labor_cost = data['labor_cost']
        if 'design_cost' in data:
            config.design_cost = data['design_cost']
        if 'manage_cost' in data:
            config.manage_cost = data['manage_cost']
        
        # 更新物料明细
        if 'materials' in data:
            # 删除原有明细
            CaseSpaceConfigItem.query.filter_by(config_id=config.id).delete()
            
            # 添加新明细
            materials = data['materials']
            total_price = 0
            
            for idx, m in enumerate(materials):
                sku_id = m.get('sku_id')
                if not sku_id:
                    continue
                    
                sku = MaterialSKU.query.get(sku_id)
                if not sku:
                    continue
                
                quantity = float(m.get('quantity', 1))
                unit_price = float(m.get('unit_price') or sku.retail_price or 0)
                item_total = quantity * unit_price
                
                item = CaseSpaceConfigItem(
                    config_id=config.id,
                    sku_id=sku_id,
                    sku_code=sku.sku_code,
                    sku_name=sku.name,
                    brand=sku.brand,
                    specification=sku.specification,
                    category=m.get('category') or sku.category,
                    quantity=quantity,
                    unit=m.get('unit') or sku.unit,
                    unit_price=unit_price,
                    total_price=item_total,
                    is_exclusive=m.get('is_exclusive', False),
                    exclusive_group=m.get('exclusive_group'),
                    is_optional=m.get('is_optional', False),
                    is_default=m.get('is_default', True),
                    sort_order=idx
                )
                
                db.session.add(item)
                total_price += item_total
            
            config.material_cost = total_price
            config.material_count = len(materials)
            config.materials = json.dumps([item.to_dict() for item in config.items])
        
        # 重新计算总价
        config.total_price = float(config.material_cost or 0) + float(config.labor_cost or 0) + float(config.design_cost or 0) + float(config.manage_cost or 0)
        
        db.session.commit()
        
        return api_response(200, '更新成功', config.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return api_response(500, f'更新失败: {str(e)}')


@space_config_bp.route('/<int:config_id>', methods=['DELETE'])
@jwt_required_v2
def delete_config(current_user, config_id):
    """删除空间配置"""
    try:
        config = CaseSpaceConfig.query.filter_by(
            id=config_id,
            tenant_id=current_user.get('tenant_id', '0')
        ).first()
        
        if not config:
            return api_response(404, '配置不存在')
        
        # 软删除（改为disabled状态）
        config.status = 'deleted'
        db.session.commit()
        
        return api_response(200, '删除成功')
        
    except Exception as e:
        db.session.rollback()
        return api_response(500, f'删除失败: {str(e)}')


# ==================== 案例空间配置查询 ====================

@space_config_bp.route('/by-case/<int:case_id>', methods=['GET'])
@jwt_required_v2
def get_case_configs(current_user, case_id):
    """获取案例的空间配置（按空间分组）"""
    try:
        configs = CaseSpaceConfig.query.filter_by(
            case_id=case_id,
            tenant_id=current_user.get('tenant_id', '0'),
            status='active'
        ).order_by(CaseSpaceConfig.space_type, CaseSpaceConfig.version_level).all()
        
        # 按空间类型分组
        grouped = {}
        for config in configs:
            space_type = config.space_type
            if space_type not in grouped:
                grouped[space_type] = []
            grouped[space_type].append(config.to_dict())
        
        return api_response(data=grouped)
        
    except Exception as e:
        return api_response(500, f'查询失败: {str(e)}')


# ==================== 模板搜索 ====================

@space_config_bp.route('/templates', methods=['GET'])
@jwt_required_v2
def search_templates(current_user):
    """搜索空间配置模板（用于新建报价）"""
    try:
        # 筛选参数
        space_type = request.args.get('space_type')
        style = request.args.get('style')
        version_level = request.args.get('version_level')
        area_min = request.args.get('area_min', type=float)
        area_max = request.args.get('area_max', type=float)
        keyword = request.args.get('keyword', '').strip()
        
        # 分页
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建查询
        query = CaseSpaceConfig.query.filter_by(
            tenant_id=current_user.get('tenant_id', '0'),
            is_template=True,
            status='active'
        )
        
        if space_type:
            query = query.filter_by(space_type=space_type)
        if version_level:
            query = query.filter_by(version_level=version_level)
        
        if area_min is not None:
            query = query.filter(CaseSpaceConfig.space_area >= area_min)
        if area_max is not None:
            query = query.filter(CaseSpaceConfig.space_area <= area_max)
        
        if keyword:
            query = query.filter(
                db.or_(
                    CaseSpaceConfig.config_name.contains(keyword),
                    CaseSpaceConfig.space_name.contains(keyword)
                )
            )
        
        if style:
            # 按案例风格筛选
            query = query.join(CaseStudy, CaseSpaceConfig.case_id == CaseStudy.id)
            query = query.filter(CaseStudy.style.contains(style))
        
        query = query.order_by(CaseSpaceConfig.total_price.asc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        items = []
        for config in pagination.items:
            data = config.to_dict()
            # 补充案例信息
            case = CaseStudy.query.get(config.case_id)
            if case:
                data['case_title'] = case.title
                data['case_style'] = case.style
                data['case_cover'] = case.cover_image
            items.append(data)
        
        return api_response(data={
            'items': items,
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        })
        
    except Exception as e:
        return api_response(500, f'搜索失败: {str(e)}')


# ==================== 版本复制 ====================

@space_config_bp.route('/<int:config_id>/clone', methods=['POST'])
@jwt_required_v2
def clone_config(current_user, config_id):
    """复制配置（同案例不同版本）"""
    try:
        source = CaseSpaceConfig.query.filter_by(
            id=config_id,
            tenant_id=current_user.get('tenant_id', '0')
        ).first()
        
        if not source:
            return api_response(404, '源配置不存在')
        
        data = request.get_json()
        target_version = data.get('version_level')
        
        if not target_version:
            return api_response(400, '缺少目标版本')
        
        # 检查目标版本是否已存在
        existing = CaseSpaceConfig.query.filter_by(
            case_id=source.case_id,
            space_type=source.space_type,
            version_level=target_version
        ).first()
        
        if existing:
            return api_response(400, f'{target_version}版本已存在')
        
        # 创建新配置
        new_config = CaseSpaceConfig(
            tenant_id=source.tenant_id,
            case_id=source.case_id,
            space_type=source.space_type,
            space_name=source.space_name,
            space_area=source.space_area,
            version_level=target_version,
            version_code=CaseSpaceConfig.get_version_code(target_version),
            config_name=source.config_name.replace(source.version_level, target_version),
            config_desc=source.config_desc,
            is_template=source.is_template,
            template_tags=source.template_tags,
            created_by=current_user.get('id')
        )
        
        db.session.add(new_config)
        db.session.flush()
        
        # 复制物料明细
        for item in source.items:
            new_item = CaseSpaceConfigItem(
                config_id=new_config.id,
                sku_id=item.sku_id,
                sku_code=item.sku_code,
                sku_name=item.sku_name,
                brand=item.brand,
                specification=item.specification,
                category=item.category,
                quantity=item.quantity,
                unit=item.unit,
                unit_price=item.unit_price,
                total_price=item.total_price,
                is_exclusive=item.is_exclusive,
                exclusive_group=item.exclusive_group,
                is_optional=item.is_optional,
                is_default=item.is_default,
                sort_order=item.sort_order
            )
            db.session.add(new_item)
        
        # 应用价格调整
        adjustment_type = data.get('adjustment_type', 'copy')
        price_adjustment = data.get('price_adjustment', 1.0)
        
        if adjustment_type == 'upgrade':
            price_adjustment = 1.5  # 升级版加价50%
        elif adjustment_type == 'downgrade':
            price_adjustment = 0.7  # 降级版减价30%
        
        new_config.material_cost = float(source.material_cost) * price_adjustment
        new_config.labor_cost = source.labor_cost
        new_config.design_cost = source.design_cost
        new_config.manage_cost = source.manage_cost
        new_config.total_price = float(new_config.material_cost) + float(new_config.labor_cost or 0) + float(new_config.design_cost or 0) + float(new_config.manage_cost or 0)
        new_config.material_count = source.material_count
        new_config.materials = json.dumps([item.to_dict() for item in new_config.items])
        
        db.session.commit()
        
        return api_response(200, '复制成功', new_config.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return api_response(500, f'复制失败: {str(e)}')


# ==================== 互斥规则管理 ====================

@space_config_bp.route('/exclusive-rules', methods=['GET'])
@jwt_required_v2
def get_exclusive_rules(current_user):
    """获取互斥规则列表"""
    try:
        rules = MaterialExclusiveRule.query.filter_by(
            tenant_id=current_user.get('tenant_id', '0'),
            is_enabled=True
        ).all()
        
        return api_response(data=[r.to_dict() for r in rules])
        
    except Exception as e:
        return api_response(500, f'查询失败: {str(e)}')


@space_config_bp.route('/exclusive-rules', methods=['POST'])
@jwt_required_v2
def create_exclusive_rule(current_user):
    """创建互斥规则"""
    try:
        data = request.get_json()
        
        rule = MaterialExclusiveRule(
            tenant_id=current_user.get('tenant_id', '0'),
            rule_name=data.get('rule_name'),
            rule_group=data.get('rule_group'),
            sku_id=data.get('sku_id'),
            exclusive_sku_ids=json.dumps(data.get('exclusive_sku_ids', [])),
            description=data.get('description')
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return api_response(200, '创建成功', rule.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return api_response(500, f'创建失败: {str(e)}')


# ==================== 兼容性检查 ====================

@space_config_bp.route('/check-compatibility', methods=['POST'])
@jwt_required_v2
def check_compatibility(current_user):
    """检查物料兼容性"""
    try:
        data = request.get_json()
        selected_sku_ids = data.get('selected_sku_ids', [])
        config_id = data.get('config_id')
        
        if not selected_sku_ids:
            return api_response(data={'compatible': True, 'conflicts': []})
        
        # 获取所有相关规则
        rules = MaterialExclusiveRule.query.filter(
            MaterialExclusiveRule.tenant_id == current_user.get('tenant_id', '0'),
            MaterialExclusiveRule.is_enabled == True,
            MaterialExclusiveRule.sku_id.in_(selected_sku_ids)
        ).all()
        
        conflicts = []
        for rule in rules:
            has_conflict, conflict_ids = rule.check_conflict(selected_sku_ids)
            if has_conflict:
                conflicts.append({
                    'rule_id': rule.id,
                    'rule_name': rule.rule_name,
                    'sku_id': rule.sku_id,
                    'conflict_sku_ids': conflict_ids,
                    'message': rule.description or f'存在互斥配置'
                })
        
        return api_response(data={
            'compatible': len(conflicts) == 0,
            'conflicts': conflicts
        })
        
    except Exception as e:
        return api_response(500, f'检查失败: {str(e)}')
