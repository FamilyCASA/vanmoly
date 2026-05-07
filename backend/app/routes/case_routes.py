# -*- coding: utf-8 -*-
"""
案例管理模块路由 V3.1
API端点: /api/v3/cases
"""

import json
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from sqlalchemy import and_, or_, desc, func

from app import db
from app.models import (
    CaseStudy, CaseMedia, CaseTimeline, CaseFile,
    CaseSubscription, CaseLead, CaseTemplate,
    CaseNotification, CaseOperationLog,
    CaseWorkflowTimeline
)
from app.models.case import MorandiPalette, PantoneColorMap
from app.models.building import Building
from app.models.hr import Employee
from app.models.service_workflow import CustomerWorkflow, WorkflowNode
from app.routes.auth_routes_v2 import jwt_required_v2
from flask import request as flask_request

case_bp = Blueprint('case', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


def log_operation(case_id, operation, content):
    """记录操作日志"""
    try:
        user = getattr(flask_request, 'current_user', None)
        log = CaseOperationLog(
            case_id=case_id,
            operator_id=user.id if user else None,
            operator_name=user.nickname if user else 'system',
            operation=operation,
            content=content,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except:
        pass


# ==================== 案例列表与详情 ====================


# ===== 颜色排序辅助函数 =====
COLOR_SORT_ORDER = {
    'red': 0, 'orange': 1, 'yellow': 2, 'beige': 3, 'pink': 4,
    'green': 5, 'blue': 6, 'brown': 7, 'gray': 8
}

def hex_to_hsl(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return (0, 0, 50)
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        max_c, min_c = max(r, g, b), min(r, g, b)
        l = (max_c + min_c) / 2 * 100
        if max_c == min_c:
            return (0, 0, l)
        d = max_c - min_c
        s = (d / (1 - abs(2*l/100 - 1))) * 100 if (1 - abs(2*l/100 - 1)) > 0 else 0
        if max_c == r:
            h = ((g - b) / d) % 6
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h = round(h * 60)
        if h < 0:
            h += 360
        return (h, s, l)
    except:
        return (0, 0, 50)

def warm_to_cool_sort_key(hex_val):
    h, s, l = hex_to_hsl(hex_val)
    if s < 10:
        return (100, l)
    if h <= 60 or h >= 300:
        return (0, -l)
    elif h <= 120:
        return (1, h)
    elif h <= 180:
        return (2, h)
    elif h <= 240:
        return (3, h)
    elif h <= 300:
        return (4, h)
    else:
        return (5, h)

@case_bp.route('/cases', methods=['GET'])
@jwt_required_v2
def get_cases(current_user):
    """获取案例列表"""
    try:
        # 分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 筛选参数
        status = request.args.get('status')
        style = request.args.get('style')
        atmosphere = request.args.get('atmosphere')  # 氛围筛选
        house_type = request.args.get('house_type')
        package_type = request.args.get('package_type')
        building_id = request.args.get('building_id', type=int)
        responsible_id = request.args.get('responsible_id', type=int)
        keyword = request.args.get('keyword')
        is_public = request.args.get('is_public', type=bool)
        is_featured = request.args.get('is_featured', type=bool)
        
        # 价格区间
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)
        
        # 面积区间
        area_min = request.args.get('area_min', type=float)
        area_max = request.args.get('area_max', type=float)
        
        # 时间范围
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # 排序
        sort_by = request.args.get('sort_by', 'updated_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 构建查询
        query = CaseStudy.query.filter(CaseStudy.deleted_at.is_(None))
        
        if status:
            # 兼容前端英文状态值 -> 数据库中文值
            STATUS_MAP = {'published': '已发布', 'draft': '草稿', 'unpublished': '已下架'}
            status = STATUS_MAP.get(status, status)
            query = query.filter(CaseStudy.status == status)
        if style:
            # 兼容前端英文风格值 -> 数据库中文值
            STYLE_MAP = {'modern': '现代', 'nordic': '北欧', 'chinese': '中式', 'luxury': '轻奢', 'american': '美式', 'european': '欧式', 'japanese': '日式'}
            style = STYLE_MAP.get(style, style)
            query = query.filter(CaseStudy.style == style)
        if atmosphere:
            query = query.filter(CaseStudy.atmosphere == atmosphere)
        
        # 颜色筛选: 支持 hex 值或色系 key
        color_filter = request.args.get('color')  # e.g. #E8C5C5 or pink
        if color_filter:
            if color_filter.startswith('#'):
                # 精确匹配 hex 色值
                color_like = f'%{color_filter}%'
                query = query.filter(or_(
                    CaseStudy.main_colors.like(color_like),
                    CaseStudy.auxiliary_colors.like(color_like),
                    CaseStudy.accent_colors.like(color_like),
                    CaseStudy.background_colors.like(color_like)
                ))
            else:
                # 按色系 key 筛选: 找该色系下所有 hex 值
                palette_colors = MorandiPalette.query.filter_by(group_key=color_filter).all()
                if palette_colors:
                    hex_values = [c.hex_value for c in palette_colors]
                    color_conditions = []
                    for hv in hex_values:
                        color_like = f'%{hv}%'
                        color_conditions.extend([
                            CaseStudy.main_colors.like(color_like),
                            CaseStudy.auxiliary_colors.like(color_like),
                            CaseStudy.accent_colors.like(color_like),
                            CaseStudy.background_colors.like(color_like)
                        ])
                    query = query.filter(or_(*color_conditions))
        if house_type:
            query = query.filter(CaseStudy.house_type == house_type)
        if package_type:
            query = query.filter(CaseStudy.package_type == package_type)
        if building_id:
            query = query.filter(CaseStudy.building_id == building_id)
        if responsible_id:
            query = query.filter(CaseStudy.responsible_id == responsible_id)
        if is_public is not None:
            query = query.filter(CaseStudy.is_public == is_public)
        if is_featured is not None:
            query = query.filter(CaseStudy.is_featured == is_featured)
        if price_min is not None:
            query = query.filter(CaseStudy.total_price >= price_min)
        if price_max is not None:
            query = query.filter(CaseStudy.total_price <= price_max)
        if area_min is not None:
            query = query.filter(CaseStudy.area >= area_min)
        if area_max is not None:
            query = query.filter(CaseStudy.area <= area_max)
        if date_from:
            query = query.filter(CaseStudy.created_at >= date_from)
        if date_to:
            query = query.filter(CaseStudy.created_at <= date_to)
        if keyword:
            query = query.filter(or_(
                CaseStudy.title.contains(keyword),
                CaseStudy.location.contains(keyword),
                CaseStudy.case_no.contains(keyword)
            ))
        
        # 排序
        sort_column = getattr(CaseStudy, sort_by, CaseStudy.updated_at)
        if sort_order == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # 分页
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        return api_response(data={
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>', methods=['GET'])
@jwt_required_v2
def get_case(current_user, id):
    """获取案例详情"""
    try:
        case = CaseStudy.query.filter_by(id=id).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')
        
        return api_response(data=case.to_dict(include_relations=True))
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/cases', methods=['POST'])
@jwt_required_v2
def create_case(current_user):
    """创建案例"""
    try:
        data = request.get_json()
        
        # 生成案例编号
        case_no = f"CS{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 处理tags字段：前端发送列表，数据库存储JSON字符串
        tags_data = data.get('tags')
        if isinstance(tags_data, list):
            tags_data = json.dumps(tags_data, ensure_ascii=False)
        
        # 处理颜色字段：前端发送列表，数据库存储JSON字符串 + 数量校验
        COLOR_LIMITS = {'main_colors': 5, 'auxiliary_colors': 5, 'accent_colors': 5, 'background_colors': 6}
        color_data = {}
        for field, limit in COLOR_LIMITS.items():
            val = data.get(field, [])
            if isinstance(val, list):
                if len(val) > limit:
                    return api_response(400, f'{field} \u6700\u591a\u53ef\u9009{limit}\u4e2a\u989c\u8272')
                color_data[field] = json.dumps(val, ensure_ascii=False)
            elif isinstance(val, str):
                color_data[field] = val
            else:
                color_data[field] = '[]'
        
        case = CaseStudy(
            case_no=case_no,
            title=data.get('title'),
            type=data.get('type', '实景'),
            style=data.get('style'),
            space_type=data.get('space_type'),
            budget_range=data.get('budget_range'),
            area=data.get('area'),
            house_type=data.get('house_type'),
            location=data.get('location'),
            building_id=data.get('building_id'),
            address=data.get('address'),
            customer_name=data.get('customer_name'),
            customer_id=data.get('customer_id'),
            cover_image=data.get('cover_image'),
            atmosphere=data.get('atmosphere'),
            vr_link=data.get('vr_link'),
            vr_qrcode=data.get('vr_qrcode'),
            planner_id=data.get('planner_id'),
            designer_id=data.get('designer_id'),
            storage_plan=data.get('storage_plan'),
            execution_detail=data.get('execution_detail'),
            description=data.get('description'),
            design_concept=data.get('design_concept'),
            whole_house_plan=data.get('whole_house_plan'),
            customer_requirements=data.get('customer_requirements'),
            design_highlights=data.get('design_highlights'),
            customer_value=data.get('customer_value'),
            tags=tags_data,
            main_colors=color_data.get('main_colors', '[]'),
            auxiliary_colors=color_data.get('auxiliary_colors', '[]'),
            accent_colors=color_data.get('accent_colors', '[]'),
            background_colors=color_data.get('background_colors', '[]'),
            total_price=data.get('total_price'),
            deal_budget=data.get('deal_budget'),
            package_type=data.get('package_type'),
            price_detail=data.get('price_detail'),
            material_list=data.get('material_list'),
            construction_phase=data.get('construction_phase'),
            owner_authorized=data.get('owner_authorized', False),
            is_public=data.get('is_public', True),
            is_top=data.get('is_top', False),
            top_position=data.get('top_position'),
            hero_images=json.dumps(data['hero_images'], ensure_ascii=False) if isinstance(data.get('hero_images'), list) else data.get('hero_images'),
            responsible_id=data.get('responsible_id'),
            status='草稿',
            created_by=current_user.get('id') if current_user else None
        )
        
        db.session.add(case)
        db.session.flush()  # 获取case.id
        
        # 处理media数组
        if 'media' in data and isinstance(data['media'], list):
            for idx, m in enumerate(data['media']):
                url = m.get('url', m) if isinstance(m, dict) else m
                media_type = m.get('media_type', 'image') if isinstance(m, dict) else 'image'
                if url:
                    description = m.get('description', '') if isinstance(m, dict) else ''
                media_record = CaseMedia(
                        case_id=case.id,
                        media_type=media_type,
                        url=url,
                        sort_order=idx,
                        description=description
                    )
            db.session.add(media_record)
            db.session.commit()
        
        # 记录日志
        log_operation(case.id, 'create', f'创建案例: {case.title}')
        
        return api_response(data=case.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_case(current_user, id):
    """更新案例"""
    try:
        case = CaseStudy.query.filter_by(id=id).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')
        
        data = request.get_json()
        
        # 更新字段
        fields = [
            'title', 'type', 'style', 'space_type', 'budget_range', 'area', 'house_type',
            'location', 'building_id', 'address', 'customer_name', 'customer_id',
            'cover_image', 'vr_link', 'vr_qrcode', 'description', 'design_concept', 'whole_house_plan',
            'customer_requirements', 'design_highlights', 'customer_value',
            'total_price', 'deal_budget', 'package_type', 'price_detail', 'material_list',
            'construction_phase', 'owner_authorized', 'is_public', 'is_featured',
            'atmosphere', 'responsible_id', 'enable_subscription', 'enable_notify',
            'planner_id', 'designer_id', 'storage_plan', 'execution_detail',
            'is_top', 'top_position'
        ]
        
        for field in fields:
            if field in data:
                setattr(case, field, data[field])
        
        # 特殊处理tags字段：前端发送列表，数据库存储JSON字符串
        if 'tags' in data:
            tags_data = data['tags']
            if isinstance(tags_data, list):
                case.tags = json.dumps(tags_data, ensure_ascii=False)
            else:
                case.tags = tags_data
        
        # 处理颜色字段
        COLOR_LIMITS = {'main_colors': 5, 'auxiliary_colors': 5, 'accent_colors': 5, 'background_colors': 6}
        for field, limit in COLOR_LIMITS.items():
            if field in data:
                val = data[field]
                if isinstance(val, list):
                    if len(val) > limit:
                        return api_response(400, f'{field} \u6700\u591a\u53ef\u9009{limit}\u4e2a\u989c\u8272')
                    setattr(case, field, json.dumps(val, ensure_ascii=False))
                elif isinstance(val, str):
                    setattr(case, field, val)
                else:
                    setattr(case, field, '[]')
        
        # 处理hero_images：前端发送JSON字符串或列表
        if 'hero_images' in data:
            hero_data = data['hero_images']
            if isinstance(hero_data, list):
                case.hero_images = json.dumps(hero_data, ensure_ascii=False)
            elif isinstance(hero_data, str):
                case.hero_images = hero_data
            else:
                case.hero_images = None
        
        # 处理gallery：前端发送JSON字符串或列表
        if 'gallery' in data:
            gallery_data = data['gallery']
            if isinstance(gallery_data, list):
                case.gallery = json.dumps(gallery_data, ensure_ascii=False)
            elif isinstance(gallery_data, str):
                case.gallery = gallery_data
            else:
                case.gallery = None
        
        # 处理media数组：写入case_media表
        if 'media' in data and isinstance(data['media'], list):
            # 先删除旧的media记录
            CaseMedia.query.filter_by(case_id=case.id).delete()
            for idx, m in enumerate(data['media']):
                url = m.get('url', m) if isinstance(m, dict) else m
                media_type = m.get('media_type', 'image') if isinstance(m, dict) else 'image'
                description = m.get('description', '') if isinstance(m, dict) else ''
                if url:
                    media_record = CaseMedia(
                        case_id=case.id,
                        media_type=media_type,
                        url=url,
                        sort_order=idx,
                        description=description
                    )
                    db.session.add(media_record)
        
        db.session.commit()
        
        # 记录日志
        log_operation(case.id, 'update', f'更新案例: {case.title}')
        
        return api_response(data=case.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_case(current_user, id):
    """删除案例（软删除）"""
    try:
        case = CaseStudy.query.filter_by(id=id).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')
        
        case.soft_delete()
        
        # 记录日志
        log_operation(case.id, 'delete', f'删除案例: {case.title}')
        
        return api_response(message='删除成功')
    except Exception as e:
        return api_response(code=500, message=str(e))


# ==================== 批量操作 ====================

@case_bp.route('/cases/batch', methods=['POST'])
@jwt_required_v2
def batch_operation(current_user):
    """批量操作"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])
        action = data.get('action')  # publish/unpublish/delete/sync_xiaohongshu/sync_mp
        
        if not ids:
            return api_response(code=400, message='请选择案例')
        
        cases = CaseStudy.query.filter(CaseStudy.id.in_(ids)).filter(CaseStudy.deleted_at.is_(None)).all()
        
        for case in cases:
            if action == 'publish':
                case.status = '已发布'
                case.publish_time = datetime.utcnow()
            elif action == 'unpublish':
                case.status = '已下架'
            elif action == 'delete':
                case.soft_delete()
            elif action == 'sync_xiaohongshu':
                case.sync_xiaohongshu = True
            elif action == 'sync_mp':
                case.sync_mp = True
            elif action == 'feature':
                case.is_featured = True
            elif action == 'unfeature':
                case.is_featured = False
        
        db.session.commit()
        
        # 记录日志
        log_operation(None, 'batch', f'批量操作: {action}, 案例数: {len(cases)}')
        
        return api_response(message=f'批量{action}成功，共{len(cases)}个案例')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ==================== 发布管理 ====================

@case_bp.route('/cases/<int:id>/publish', methods=['POST'])
@jwt_required_v2
def publish_case(current_user, id):
    """立即发布"""
    try:
        case = CaseStudy.query.filter_by(id=id).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')
        
        case.status = '已发布'
        case.publish_time = datetime.utcnow()
        db.session.commit()
        
        log_operation(case.id, 'publish', f'发布案例: {case.title}')
        
        return api_response(message='发布成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/schedule', methods=['POST'])
@jwt_required_v2
def schedule_case(current_user, id):
    """定时发布"""
    try:
        case = CaseStudy.query.filter_by(id=id).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')
        
        data = request.get_json()
        scheduled_time = data.get('scheduled_time')
        
        case.scheduled_time = scheduled_time
        db.session.commit()
        
        log_operation(case.id, 'schedule', f'定时发布案例: {case.title}, 时间: {scheduled_time}')
        
        return api_response(message='定时发布设置成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/unpublish', methods=['POST'])
@jwt_required_v2
def unpublish_case(current_user, id):
    """下架"""
    try:
        case = CaseStudy.query.filter_by(id=id).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')
        
        case.status = '已下架'
        db.session.commit()
        
        log_operation(case.id, 'unpublish', f'下架案例: {case.title}')
        
        return api_response(message='下架成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/feature', methods=['POST'])
@jwt_required_v2
def toggle_feature_case(current_user, id):
    """设置/取消置顶"""
    try:
        case = CaseStudy.query.filter_by(id=id).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')
        
        data = request.get_json() or {}
        is_featured = data.get('is_featured', not case.is_featured)
        
        case.is_featured = is_featured
        db.session.commit()
        
        action = '置顶' if is_featured else '取消置顶'
        log_operation(case.id, 'feature', f'{action}案例: {case.title}')
        
        return api_response(data=case.to_dict(), message=f'{action}成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ==================== 时间轴管理 ====================

@case_bp.route('/cases/<int:id>/timeline', methods=['GET'])
@jwt_required_v2
def get_timeline(current_user, id):
    """获取案例时间轴"""
    try:
        case = CaseStudy.query.filter_by(id=id).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')
        
        timeline = CaseTimeline.query.filter_by(case_id=id).order_by(CaseTimeline.node_time).all()
        return api_response(data=[t.to_dict() for t in timeline])
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/timeline', methods=['POST'])
@jwt_required_v2
def add_timeline_node(current_user, id):
    """添加时间节点"""
    try:
        case = CaseStudy.query.filter_by(id=id).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')
        
        data = request.get_json()
        
        # 解析 datetime 字符串（SQLite DateTime 只接受 Python datetime 对象）
        node_time_str = data.get('node_time')
        node_time = None
        if node_time_str:
            # 支持 ISO 格式带 Z / 不带 Z / 标准格式
            ts = node_time_str.replace('Z', '+00:00')
            node_time = datetime.fromisoformat(ts)
        
        node = CaseTimeline(
            case_id=id,
            node_time=node_time,
            title=data.get('title'),
            content=data.get('content'),
            media_urls=data.get('media_urls'),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(node)
        db.session.commit()
        
        return api_response(data=node.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/timeline/<int:node_id>', methods=['PUT'])
@jwt_required_v2
def update_timeline_node(current_user, node_id):
    """鏇存柊鏃堕棿鑺傜偣"""
    try:
        node = CaseTimeline.query.get(node_id)
        if not node:
            return api_response(code=404, message='鑺傜偣涓嶅瓨鍦?')
        
        data = request.get_json()
        
        if 'node_time' in data:
            node_time_str = data['node_time']
            if node_time_str:
                ts = node_time_str.replace('Z', '+00:00')
                node.node_time = datetime.fromisoformat(ts)
            else:
                node.node_time = None
        if 'title' in data:
            node.title = data['title']
        if 'content' in data:
            node.content = data['content']
        if 'media_urls' in data:
            node.media_urls = data['media_urls']
        if 'sort_order' in data:
            node.sort_order = data['sort_order']
        
        db.session.commit()
        
        return api_response(data=node.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/timeline/<int:node_id>', methods=['DELETE'])
@jwt_required_v2
def delete_timeline_node(current_user, node_id):
    """删除鏃堕棿鑺傜偣"""
    try:
        node = CaseTimeline.query.get(node_id)
        if not node:
            return api_response(code=404, message='鑺傜偣涓嶅瓨鍦?')
        
        db.session.delete(node)
        db.session.commit()
        
        return api_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ==================== 鏂囦欢绠悊 ====================

@case_bp.route('/cases/<int:id>/files', methods=['GET'])
@jwt_required_v2
def get_files(current_user, id):
    """获取妗堜緥鏂囦欢"""
    try:
        files = CaseFile.query.filter_by(case_id=id).all()
        return api_response(data=[f.to_dict() for f in files])
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/files', methods=['POST'])
@jwt_required_v2
def add_file(current_user, id):
    """添加鏂囦欢"""
    try:
        data = request.get_json()
        
        file = CaseFile(
            case_id=id,
            file_type=data.get('file_type'),
            file_name=data.get('file_name'),
            file_url=data.get('file_url'),
            has_watermark=data.get('has_watermark', False)
        )
        
        db.session.add(file)
        db.session.commit()
        
        return api_response(data=file.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/files/<int:file_id>', methods=['DELETE'])
@jwt_required_v2
def delete_file(current_user, file_id):
    """删除鏂囦欢"""
    try:
        file = CaseFile.query.get(file_id)
        if not file:
            return api_response(code=404, message='鏂囦欢涓嶅瓨鍦?')
        
        db.session.delete(file)
        db.session.commit()
        
        return api_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/files/<int:file_id>/download', methods=['GET'])
@jwt_required_v2
def download_file(current_user, file_id):
    """涓嬭浇鏂囦欢"""
    try:
        file = CaseFile.query.get(file_id)
        if not file:
            return api_response(code=404, message='鏂囦欢涓嶅瓨鍦?')
        
        # 增加涓嬭浇璁暟
        file.download_count += 1
        db.session.commit()
        
        return api_response(data={'download_url': file.file_url, 'file_name': file.file_name})
    except Exception as e:
        return api_response(code=500, message=str(e))


# ==================== 线索管理 ====================

@case_bp.route('/cases/<int:id>/leads', methods=['GET'])
@jwt_required_v2
def get_case_leads(current_user, id):
    """获取案例留资"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status')
        
        query = CaseLead.query.filter_by(case_id=id)
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(desc(CaseLead.created_at)).paginate(
            page=page, per_page=page_size, error_out=False
        )
        
        return api_response(data={
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/case-leads', methods=['GET'])
@jwt_required_v2
def get_all_leads(current_user):
    """获取鍏儴鐣欒祫"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        case_id = request.args.get('case_id', type=int)
        status = request.args.get('status')
        source = request.args.get('source')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = CaseLead.query
        
        if case_id:
            query = query.filter_by(case_id=case_id)
        if status:
            query = query.filter_by(status=status)
        if source:
            query = query.filter_by(source=source)
        if date_from:
            query = query.filter(CaseLead.created_at >= date_from)
        if date_to:
            query = query.filter(CaseLead.created_at <= date_to)
        
        pagination = query.order_by(desc(CaseLead.created_at)).paginate(
            page=page, per_page=page_size, error_out=False
        )
        
        return api_response(data={
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/case-leads/<int:lead_id>/contact', methods=['POST'])
@jwt_required_v2
def mark_lead_contacted(current_user, lead_id):
    """鏍囪鐣欒祫宸茶仈绯?"""
    try:
        lead = CaseLead.query.get(lead_id)
        if not lead:
            return api_response(code=404, message='鐣欒祫涓嶅瓨鍦?')
        
        lead.status = 'contacted'
        lead.contacted_at = datetime.utcnow()
        
        data = request.get_json()
        if data and 'remark' in data:
            lead.remark = data['remark']
        
        db.session.commit()
        
        return api_response(data=lead.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/case-leads/<int:lead_id>/convert', methods=['POST'])
@jwt_required_v2
def mark_lead_converted(current_user, lead_id):
    """标记留资已转化"""
    try:
        lead = CaseLead.query.get(lead_id)
        if not lead:
            return api_response(code=404, message='鐣欒祫涓嶅瓨鍦?')
        
        lead.status = 'converted'
        lead.converted_at = datetime.utcnow()
        
        db.session.commit()
        
        return api_response(data=lead.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ==================== 模板库 ====================

@case_bp.route('/case-templates', methods=['GET'])
@jwt_required_v2
def get_templates(current_user):
    """获取模板列表"""
    try:
        templates = CaseTemplate.query.order_by(desc(CaseTemplate.created_at)).all()
        return api_response(data=[t.to_dict() for t in templates])
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/case-templates', methods=['POST'])
@jwt_required_v2
def create_template(current_user):
    """创建模板"""
    try:
        data = request.get_json()
        template = CaseTemplate(
            template_name=data.get('template_name'),
            package_type=data.get('package_type'),
            price_min=data.get('price_min'),
            price_max=data.get('price_max'),
            suitable_house_types=data.get('suitable_house_types'),
            base_content=data.get('base_content'),
            sample_images=data.get('sample_images'),
            created_by=current_user.get('id') if current_user else None
        )
        
        db.session.add(template)
        db.session.commit()
        
        return api_response(data=template.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/case-templates/<int:id>', methods=['GET'])
@jwt_required_v2
def get_template(current_user, id):
    """获取模板详情"""
    try:
        template = CaseTemplate.query.get(id)
        if not template:
            return api_response(code=404, message='模板不存在')
        
        return api_response(data=template.to_dict())
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/case-templates/<int:id>', methods=['PUT'])
@jwt_required_v2
def update_template(current_user, id):
    """更新模板"""
    try:
        template = CaseTemplate.query.get(id)
        if not template:
            return api_response(code=404, message='模板不存在')
        
        data = request.get_json()
        
        fields = ['template_name', 'package_type', 'price_min', 'price_max',
                  'suitable_house_types', 'base_content', 'sample_images']
        
        for field in fields:
            if field in data:
                setattr(template, field, data[field])
        
        db.session.commit()
        
        return api_response(data=template.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/case-templates/<int:id>', methods=['DELETE'])
@jwt_required_v2
def delete_template(current_user, id):
    """删除模板"""
    try:
        template = CaseTemplate.query.get(id)
        if not template:
            return api_response(code=404, message='模板不存在')
        
        db.session.delete(template)
        db.session.commit()
        
        return api_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/case-templates/<int:id>/use', methods=['POST'])
@jwt_required_v2
def use_template(current_user, id):
    """浣跨敤模板创建妗堜緥"""
    try:
        template = CaseTemplate.query.get(id)
        if not template:
            return api_response(code=404, message='模板不存在')
        
        data = request.get_json()
        # use current_user from decorator
        
        # 解析模板基础内容
        base_content = {}
        if template.base_content:
            import json
            try:
                base_content = json.loads(template.base_content)
            except:
                pass
        
        # 鐢熸垚妗堜緥缂栧彿
        case_no = f"CS{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        case = CaseStudy(
            case_no=case_no,
            title=data.get('title', base_content.get('title', '新案例')),
            type=data.get('type', base_content.get('type', '实景')),
            style=data.get('style', base_content.get('style')),
            house_type=data.get('house_type', base_content.get('house_type')),
            package_type=template.package_type,
            total_price=data.get('total_price'),
            design_concept=base_content.get('design_concept'),
            whole_house_plan=base_content.get('whole_house_plan'),
            customer_requirements=base_content.get('customer_requirements'),
            design_highlights=base_content.get('design_highlights'),
            customer_value=base_content.get('customer_value'),
            status='草稿',
            created_by=current_user.get('id') if current_user else None
        )
        
        db.session.add(case)
        db.session.commit()
        
        log_operation(case.id, 'create_from_template', f'使用模板 {template.template_name} 创建案例')
        
        return api_response(data=case.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ==================== 数据统计 ====================

@case_bp.route('/cases/<int:id>/stats', methods=['GET'])
@jwt_required_v2
def get_case_stats(current_user, id):
    """获取单个案例统计"""
    try:
        case = CaseStudy.query.filter_by(id=id).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')
        
        return api_response(data={
            'view_count': case.view_count,
            'like_count': case.like_count,
            'subscription_count': case.subscription_count,
            'lead_count': case.lead_count,
            'consult_count': case.consult_count,
            'download_count': case.download_count,
            'share_count': case.share_count
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/stats/overview', methods=['GET'])
@jwt_required_v2
def get_stats_overview(current_user):
    """获取鍏眬妗堜緥缁熻"""
    try:
        # 鍩虹缁熻
        total_cases = CaseStudy.query.filter(CaseStudy.deleted_at.is_(None)).count()
        published_cases = CaseStudy.query.filter_by(status='已发布').filter(CaseStudy.deleted_at.is_(None)).count()
        draft_cases = CaseStudy.query.filter_by(status='草稿').filter(CaseStudy.deleted_at.is_(None)).count()
        
        # 数据统计
        total_views = db.session.query(func.sum(CaseStudy.view_count)).scalar() or 0
        total_likes = db.session.query(func.sum(CaseStudy.like_count)).scalar() or 0
        total_subscriptions = db.session.query(func.sum(CaseStudy.subscription_count)).scalar() or 0
        total_leads = db.session.query(func.sum(CaseStudy.lead_count)).scalar() or 0
        
        # 鏈湀鏂板
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_new_cases = CaseStudy.query.filter(
            CaseStudy.created_at >= month_start,
            CaseStudy.deleted_at.is_(None)
        ).count()
        
        return api_response(data={
            'total_cases': total_cases,
            'published_cases': published_cases,
            'draft_cases': draft_cases,
            'total_views': int(total_views),
            'total_likes': int(total_likes),
            'total_subscriptions': int(total_subscriptions),
            'total_leads': int(total_leads),
            'month_new_cases': month_new_cases
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


# ==================== 前台 API（无需登录） ====================

@case_bp.route('/public/cases', methods=['GET'])
def get_public_cases():
    """获取公开案例列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 12, type=int)
        style = request.args.get('style')
        house_type = request.args.get('house_type')
        package_type = request.args.get('package_type')
        atmosphere = request.args.get('atmosphere')  # 氛围筛选
        progress = request.args.get('progress')  # 进度筛选: designing/construction/completed
        
        query = CaseStudy.query.filter_by(status='已发布', is_public=True).filter(CaseStudy.deleted_at.is_(None))
        
        if style:
            query = query.filter(CaseStudy.style == style)
        if house_type:
            query = query.filter(CaseStudy.house_type == house_type)
        if package_type:
            query = query.filter(CaseStudy.package_type == package_type)
        if atmosphere:
            query = query.filter(CaseStudy.atmosphere == atmosphere)
        
        # 颜色筛选: 支持 hex 值或色系 key
        color_filter = request.args.get('color')
        if color_filter:
            if color_filter.startswith('#'):
                color_like = f'%{color_filter}%'
                query = query.filter(or_(
                    CaseStudy.main_colors.like(color_like),
                    CaseStudy.auxiliary_colors.like(color_like),
                    CaseStudy.accent_colors.like(color_like),
                    CaseStudy.background_colors.like(color_like)
                ))
            else:
                palette_colors = MorandiPalette.query.filter_by(group_key=color_filter).all()
                if palette_colors:
                    hex_values = [c.hex_value for c in palette_colors]
                    color_conditions = []
                    for hv in hex_values:
                        color_like = f'%{hv}%'
                        color_conditions.extend([
                            CaseStudy.main_colors.like(color_like),
                            CaseStudy.auxiliary_colors.like(color_like),
                            CaseStudy.accent_colors.like(color_like),
                            CaseStudy.background_colors.like(color_like)
                        ])
                    query = query.filter(or_(*color_conditions))
        
        # progress filter - 支持6个独立阶段 + real_case + designing(兼容旧前端)
        if progress:
            if progress == 'real_case':
                query = query.filter(CaseStudy.is_real_case == True)
            elif progress in ('acquisition', 'conversion', 'preparation', 
                              'construction', 'soft_service', 'after_sales'):
                # 单阶段筛选：查找该阶段有 ongoing 节点的案例
                query = query.filter(CaseStudy.is_real_case == True)
                phase_ids = db.session.query(CaseWorkflowTimeline.case_id).filter(
                    CaseWorkflowTimeline.status == 'ongoing',
                    CaseWorkflowTimeline.phase == progress
                ).subquery()
                query = query.filter(CaseStudy.id.in_(phase_ids))
            elif progress == 'designing':
                # 兼容旧参数：acquisition+conversion+preparation 合计
                query = query.filter(CaseStudy.is_real_case == True)
                designing_ids = db.session.query(CaseWorkflowTimeline.case_id).filter(
                    CaseWorkflowTimeline.status == 'ongoing',
                    CaseWorkflowTimeline.phase.in_(['acquisition', 'conversion', 'preparation'])
                ).subquery()
                query = query.filter(CaseStudy.id.in_(designing_ids))
        
        # 排序：精选优先，按发布时间倒序
        query = query.order_by(desc(CaseStudy.is_featured), desc(CaseStudy.publish_time))
        
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        items = []
        for item in pagination.items:
            d = item.to_dict()
            # add building_name for real cases
            if item.building_id and item.is_real_case:
                building = Building.query.get(item.building_id)
                if building:
                    d['building_name'] = building.name
            # add lightweight workflow progress for list view
            if item.is_real_case:
                tl_nodes = CaseWorkflowTimeline.query.filter_by(case_id=item.id).order_by(
                    CaseWorkflowTimeline.phase_order
                ).all()
                if tl_nodes:
                    total = len(tl_nodes)
                    completed = sum(1 for n in tl_nodes if n.status == 'completed')
                    ongoing_nodes = [n for n in tl_nodes if n.status == 'ongoing']
                    ongoing_count = len(ongoing_nodes)
                    pct = round(completed / total * 100) if total > 0 else 0
                    cur_phase = ''
                    ongoing_node_names = []
                    if ongoing_nodes:
                        cur_phase = ongoing_nodes[0].phase
                        ongoing_node_names = [n.node_name for n in ongoing_nodes]
                    elif completed > 0:
                        last_done = [n for n in tl_nodes if n.status == 'completed'][-1]
                        cur_phase = last_done.phase
                    d['workflow_progress'] = {
                        'progress_pct': pct,
                        'current_phase': cur_phase,
                        'ongoing_node_names': ongoing_node_names,
                        'completed_nodes': completed,
                        'ongoing_nodes': ongoing_count,
                        'total_nodes': total
                    }
            items.append(d)
        
        return api_response(data={
            'items': items,
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/public/cases/<int:id>', methods=['GET'])
def get_public_case(id):
    """获取公开案例详情"""
    try:
        case = CaseStudy.query.filter_by(
            id=id, status='已发布', is_public=True
        ).filter(CaseStudy.deleted_at.is_(None)).first()
        
        if not case:
            return api_response(code=404, message='案例不存在')
        
        # 增加浏览量
        case.increment_view()
        
        return api_response(data=case.to_dict(include_relations=True))
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/public/cases/<int:id>/like', methods=['POST'])
def like_case(id):
    """点赞案例"""
    try:
        case = CaseStudy.query.filter_by(
            id=id, status='已发布', is_public=True
        ).filter(CaseStudy.deleted_at.is_(None)).first()
        
        if not case:
            return api_response(code=404, message='案例不存在')
        
        case.increment_likes()
        
        return api_response(data={'like_count': case.like_count})
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/public/cases/<int:id>/subscription-status', methods=['GET'])
def get_subscription_status(id):
    """查询订阅状态"""
    try:
        case = CaseStudy.query.filter_by(
            id=id, status='已发布', is_public=True
        ).filter(CaseStudy.deleted_at.is_(None)).first()
        if not case:
            return api_response(code=404, message='案例不存在')

        phone = request.args.get('phone')
        openid = request.args.get('openid')
        email = request.args.get('email')

        # phone/openid/email 可选，未提供时视为未订阅
        if not phone and not openid and not email:
            return api_response(data={'is_subscribed': False, 'notify_enabled': True})

        query = CaseSubscription.query.filter_by(case_id=id)
        sub = None
        if phone:
            sub = query.filter_by(phone=phone).first()
        if not sub and email:
            sub = query.filter_by(email=email).first()
        if not sub:
            sub = query.filter_by(openid=openid).first()

        return api_response(data={
            'is_subscribed': sub is not None,
            'notify_enabled': sub.notify_enabled if sub else True,
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/public/cases/<int:id>/subscribe', methods=['POST'])
def subscribe_case(id):
    """订阅案例"""
    try:
        case = CaseStudy.query.filter_by(
            id=id, status='已发布', is_public=True
        ).filter(CaseStudy.deleted_at.is_(None)).first()
        
        if not case:
            return api_response(code=404, message='案例不存在')
        
        data = request.get_json() or {}
        openid = data.get('openid')
        phone = data.get('phone')
        email = data.get('email')

        if not openid and not phone and not email:
            return api_response(code=400, message='openid/phone/email required')
        
        # 检查是否已订阅
        query = CaseSubscription.query.filter_by(case_id=id)
        existing = None
        if openid:
            existing = query.filter_by(openid=openid).first()
        if not existing and phone:
            existing = query.filter_by(phone=phone).first()
        if not existing and email:
            existing = query.filter_by(email=email).first()
        
        if existing:
            return api_response(code=400, message='已订阅该案例')
        
        # 创建订阅
        subscription = CaseSubscription(
            case_id=id,
            openid=openid,
            phone=phone,
            email=email,
            notify_enabled=True
        )
        
        db.session.add(subscription)
        
        # 增加订阅数
        case.subscription_count += 1
        
        db.session.commit()
        
        return api_response(message='订阅成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))



@case_bp.route('/public/cases/<int:id>/lead', methods=['POST'])
def create_case_lead(id):
    """提交留资"""
    try:
        case = CaseStudy.query.filter_by(
            id=id, status='已发布', is_public=True
        ).filter(CaseStudy.deleted_at.is_(None)).first()
        
        if not case:
            return api_response(code=404, message='案例不存在')
        
        data = request.get_json()
        
        lead = CaseLead(
            case_id=id,
            name=data.get('name'),
            phone=data.get('phone'),
            email=data.get('email'),
            wechat=data.get('wechat'),
            source=data.get('source', 'consult'),
            message=data.get('message')
        )
        
        db.session.add(lead)
        
        # 增加留资数
        case.lead_count += 1
        
        db.session.commit()
        
        return api_response(message='提交成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/public/cases/filters', methods=['GET'])
def get_case_filters():
    """获取案例筛选选项"""
    try:
        # 风格列表
        styles = db.session.query(CaseStudy.style).distinct().filter(
            CaseStudy.style.isnot(None),
            CaseStudy.status == '已发布',
            CaseStudy.is_public == True
        ).all()
        
        # 户型列表
        house_types = db.session.query(CaseStudy.house_type).distinct().filter(
            CaseStudy.house_type.isnot(None),
            CaseStudy.status == '已发布',
            CaseStudy.is_public == True
        ).all()
        
        # 套餐列表
        packages = db.session.query(CaseStudy.package_type).distinct().filter(
            CaseStudy.package_type.isnot(None),
            CaseStudy.status == '已发布',
            CaseStudy.is_public == True
        ).all()
        
        # 氛围统计
        atmospheres_raw = db.session.query(
            CaseStudy.atmosphere,
            func.count(CaseStudy.id).label('count')
        ).filter(
            CaseStudy.atmosphere.isnot(None),
            CaseStudy.status == '已发布',
            CaseStudy.is_public == True
        ).group_by(CaseStudy.atmosphere).all()
        
        atmospheres = [{'key': a[0], 'count': a[1]} for a in atmospheres_raw if a[0]]
        
        # progress counts - 返回6个独立阶段的准确计数（基于 ongoing 节点）
        real_case_count = CaseStudy.query.filter_by(
            status='已发布', is_public=True, is_real_case=True
        ).filter(CaseStudy.deleted_at.is_(None)).count()
        
        # 各阶段独立计数：统计该阶段有 ongoing 节点的案例数
        phase_counts = {}
        for phase_code in ['acquisition', 'conversion', 'preparation', 
                          'construction', 'soft_service', 'after_sales']:
            cnt = db.session.query(
                CaseWorkflowTimeline.case_id
            ).filter(
                CaseWorkflowTimeline.status == 'ongoing',
                CaseWorkflowTimeline.phase == phase_code
            ).distinct().count()
            phase_counts[f'{phase_code}_count'] = cnt
        
        return api_response(data={
            'styles': [s[0] for s in styles if s[0]],
            'house_types': [h[0] for h in house_types if h[0]],
            'packages': [p[0] for p in packages if p[0]],
            'atmospheres': atmospheres,
            'progress_options': [
                {'key': 'real_case', 'label': '真实案例', 'count': real_case_count},
                {'key': 'acquisition_count', 'label': '获客沉淀', 'count': phase_counts.get('acquisition_count', 0)},
                {'key': 'conversion_count', 'label': '转化签约', 'count': phase_counts.get('conversion_count', 0)},
                {'key': 'preparation_count', 'label': '前期准备', 'count': phase_counts.get('preparation_count', 0)},
                {'key': 'construction', 'label': '硬装施工', 'count': phase_counts.get('construction_count', 0)},
                {'key': 'soft_service', 'label': '软装服务', 'count': phase_counts.get('soft_service_count', 0)},
                {'key': 'after_sales_count', 'label': '售后服务', 'count': phase_counts.get('after_sales_count', 0)}
            ]
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


# ==================== 精选推荐 API ====================

@case_bp.route('/cases/featured', methods=['GET'])
def get_featured_cases():
    """获取精选推荐"""
    try:
        limit = request.args.get('limit', 6, type=int)
        
        cases = CaseStudy.query.filter_by(
            status='已发布', is_public=True, is_featured=True
        ).filter(CaseStudy.deleted_at.is_(None)).order_by(
            desc(CaseStudy.publish_time)
        ).limit(limit).all()
        
        return api_response(data=[item.to_dict() for item in cases])
    except Exception as e:
        return api_response(code=500, message=str(e))


# ==================== 测试路由 ====================

@case_bp.route('/test-db', methods=['GET'])
def test_db():
    """测试数据库连接"""
    try:
        count = CaseTemplate.query.count()
        return api_response(data={'count': count, 'message': 'Database OK'})
    except Exception as e:
        import traceback
        return api_response(code=500, message=f'{str(e)}\n{traceback.format_exc()}')


# ==================== Workflow Timeline ====================

@case_bp.route('/cases/<int:id>/workflow/init', methods=['POST'])
@jwt_required_v2
def init_case_workflow(id):
    """Initialize workflow timeline for a case.
    Requires: case has customer_id + building_id + a valid workflow_id.
    Creates timeline entries from workflow nodes."""
    cs = CaseStudy.query.get_or_404(id)
    if not (cs.customer_id and cs.building_id):
        return api_response(code=400, message='Case must link to customer and building')

    # Determine workflow
    if cs.workflow_id:
        wf = CustomerWorkflow.query.get(cs.workflow_id)
    else:
        wf = CustomerWorkflow.query.filter_by(customer_id=cs.customer_id, is_deleted=False).first()
        if wf:
            cs.workflow_id = wf.id

    if not wf:
        return api_response(code=400, message='No service workflow found for this case')

    # Check if already initialized
    existing = CaseWorkflowTimeline.query.filter_by(case_id=id).first()
    if existing:
        return api_response(code=409, message='Workflow timeline already initialized')

    # Get all enabled workflow nodes ordered
    nodes = WorkflowNode.query.filter_by(
        is_enabled=True
    ).order_by(WorkflowNode.phase_order, WorkflowNode.sort_order).all()

    if not nodes:
        return api_response(code=400, message='No workflow nodes defined')

    # Create timeline entries
    for node in nodes:
        tl = CaseWorkflowTimeline(
            case_id=id,
            workflow_id=wf.id,
            node_id=node.id,
            node_code=node.node_code,
            node_name=node.node_name,
            phase=node.phase,
            phase_order=node.phase_order,
            status='pending'
        )
        db.session.add(tl)

    cs.is_real_case = True
    cs.workflow_id = wf.id
    db.session.commit()

    timeline = CaseWorkflowTimeline.query.filter_by(case_id=id).order_by(
        CaseWorkflowTimeline.phase_order
    ).all()
    return api_response(data={
        'message': 'Workflow timeline initialized',
        'total_nodes': len(timeline),
        'timeline': [t.to_dict() for t in timeline]
    })


@case_bp.route('/cases/<int:id>/workflow/timeline', methods=['GET'])
def get_case_workflow_timeline(id):
    """Get workflow timeline for a case (public read)."""
    cs = CaseStudy.query.get_or_404(id)
    timeline = CaseWorkflowTimeline.query.filter_by(case_id=id).order_by(
        CaseWorkflowTimeline.phase_order
    ).all()
    return api_response(data={
        'case_id': id,
        'enable_public_workflow': cs.enable_public_workflow,
        'is_real_case': cs.is_real_case,
        'timeline': [t.to_dict() for t in timeline]
    })


@case_bp.route('/cases/<int:id>/workflow/timeline', methods=['POST'])
@jwt_required_v2
def update_case_workflow_timeline(id):
    """Update a timeline node status, photos, notes."""
    data = flask_request.get_json()
    tl_id = data.get('timeline_id')
    if not tl_id:
        return api_response(code=400, message='timeline_id required')

    tl = CaseWorkflowTimeline.query.filter_by(id=tl_id, case_id=id).first_or_404()

    if 'status' in data and data['status'] in ('pending', 'ongoing', 'completed'):
        tl.status = data['status']
        if data['status'] == 'ongoing' and not tl.start_time:
            tl.start_time = datetime.utcnow()
        if data['status'] == 'completed' and not tl.end_time:
            tl.end_time = datetime.utcnow()

    if 'photos' in data:
        tl.photos = json.dumps(data['photos'], ensure_ascii=False)
    if 'renderings' in data:
        tl.renderings = json.dumps(data['renderings'], ensure_ascii=False)
    if 'notes' in data:
        tl.notes = data['notes']
    if 'is_public' in data:
        tl.is_public = data['is_public']

    db.session.commit()
    return api_response(data=tl.to_dict())


@case_bp.route('/cases/<int:id>/workflow/authorize', methods=['POST'])
@jwt_required_v2
def authorize_case_workflow(id):
    """Update case workflow authorization (public visibility toggle)."""
    data = flask_request.get_json()
    cs = CaseStudy.query.get_or_404(id)

    if not cs.is_real_case:
        return api_response(code=400, message='Only real cases can be authorized')

    enable = data.get('enable_public_workflow', cs.enable_public_workflow)
    cs.enable_public_workflow = enable
    cs.owner_authorized = enable
    db.session.commit()

    return api_response(data={
        'case_id': id,
        'enable_public_workflow': cs.enable_public_workflow,
        'owner_authorized': cs.owner_authorized
    })


@case_bp.route('/cases/<int:id>/workflow/photos', methods=['POST'])
@jwt_required_v2
def upload_case_workflow_photo(id):
    """Upload photo to a specific timeline node.
    Accepts form: timeline_id, file, type (photo/rendering)."""
    tl_id = flask_request.form.get('timeline_id')
    photo_type = flask_request.form.get('type', 'photo')

    if not tl_id:
        return api_response(code=400, message='timeline_id required')

    tl = CaseWorkflowTimeline.query.filter_by(id=tl_id, case_id=id).first_or_404()

    file = flask_request.files.get('file')
    if not file:
        return api_response(code=400, message='file required')

    # Reuse existing upload logic
    try:
        from app.utils.upload import save_upload_file
        result = save_upload_file(file, category='image', custom_name=f'wf_{id}_node_{tl_id}')
        if not result.get('success'):
            return api_response(code=500, message=result.get('error', 'Upload failed'))
        file_url = result.get('file_url', '')
    except Exception as e:
        return api_response(code=500, message=f'Upload failed: {str(e)}')

    # Append to the correct list
    if photo_type == 'rendering':
        photos = json.loads(tl.renderings) if tl.renderings else []
        photos.append(file_url)
        tl.renderings = json.dumps(photos, ensure_ascii=False)
    else:
        photos = json.loads(tl.photos) if tl.photos else []
        photos.append(file_url)
        tl.photos = json.dumps(photos, ensure_ascii=False)

    db.session.commit()
    return api_response(data={
        'timeline_id': tl_id,
        'type': photo_type,
        'file_url': file_url,
        'photos': json.loads(tl.photos),
        'renderings': json.loads(tl.renderings)
    })


# ==================== Workflow Nodes Template ====================

@case_bp.route('/workflow/nodes', methods=['GET'])
@jwt_required_v2
def get_workflow_nodes(current_user):
    """获取流程节点模板列表（用于时间轴节点选择）"""
    try:
        nodes = WorkflowNode.query.filter_by(
            is_enabled=True
        ).order_by(WorkflowNode.phase_order, WorkflowNode.sort_order).all()
        
        return api_response(data={
            'items': [{
                'id': n.id,
                'node_code': n.node_code,
                'node_name': n.node_name,
                'phase': n.phase,
                'phase_order': n.phase_order,
                'sort_order': n.sort_order,
                'description': n.description or ''
            } for n in nodes]
        })
    except Exception as e:
        import traceback
        return api_response(code=500, message=f'{str(e)}\n{traceback.format_exc()}')



@case_bp.route('/color-index', methods=['GET'])
def get_color_index():
    """获取所有案例色值索引（暖→冷→灰排序），用于前台色条展示
    返回所有在已发布案例中使用过的色值，以及完整莫兰迪色卡，按暖色→冷色→灰度排序
    """
    try:
        from app.models.case import CaseStudy, MorandiPalette
        
        # 1. Get all unique colors from published cases
        cases = CaseStudy.query.filter_by(status='已发布').all()
        hex_counts = {}
        for case in cases:
            for field in ['main_colors', 'auxiliary_colors', 'accent_colors', 'background_colors']:
                raw = getattr(case, field, None)
                if raw and raw not in ('[]', ''):
                    try:
                        arr = json.loads(raw)
                        for item in arr:
                            if isinstance(item, dict) and item.get('hex'):
                                h = item['hex'].upper()
                                hex_counts[h] = hex_counts.get(h, 0) + 1
                    except:
                        pass
        
        # 2. Get full morandi palette
        palette = {c.hex_value.upper(): c for c in MorandiPalette.query.all()}
        
        # 3. Merge: all palette colors + case colors
        all_hex = set(list(palette.keys()) + list(hex_counts.keys()))
        
        # 4. Sort: warm→cool→gray
        sorted_hex = sorted(all_hex, key=warm_to_cool_sort_key)
        
        # 5. Build result with weight (case frequency) and pantone info
        result = []
        for h in sorted_hex:
            h_upper = h.upper()
            pantone_name = ''
            pantone_code = ''
            if h_upper in palette:
                pantone_name = palette[h_upper].name_cn or ''
                pantone_code = palette[h_upper].pantone_code or ''
            weight = hex_counts.get(h_upper, 0)
            result.append({
                'hex': h_upper,
                'pantone_name': pantone_name,
                'pantone_code': pantone_code,
                'count': weight
            })
        
        return api_response(data={'colors': result, 'total': len(result)})
    except Exception as e:
        return api_response(code=500, message=str(e))


# ========== 色卡与配色 API ==========

@case_bp.route('/morandi-palette', methods=['GET'])
def get_morandi_palette():
    """获取莫兰迪色卡数据，按色系分组"""
    try:
        colors = MorandiPalette.query.order_by(MorandiPalette.group_key, MorandiPalette.sort_order).all()
        # 按色系分组
        groups = {}
        for c in colors:
            if c.group_key not in groups:
                groups[c.group_key] = {
                    'key': c.group_key,
                    'name': c.group_name,
                    'colors': []
                }
            groups[c.group_key]['colors'].append(c.to_dict())
        result = list(groups.values())
        return api_response(data=result)
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/pantone-colors', methods=['GET'])
def get_pantone_colors():
    """获取潘通色号映射表"""
    try:
        mappings = PantoneColorMap.query.order_by(PantoneColorMap.pantone_code).all()
        result = [m.to_dict() for m in mappings]
        return api_response(data=result)
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/pantone-lookup', methods=['GET'])
def pantone_lookup():
    """根据潘通色号查找对应色值"""
    try:
        code = request.args.get('code', '').strip()
        if not code:
            return api_response(code=400, message='\u8bf7\u63d0\u4f9b\u6f58\u901a\u8272\u53f7')
        # Try exact match, then with PANTONE prefix, then LIKE partial match
        mapping = PantoneColorMap.query.filter_by(pantone_code=code).first()
        if not mapping and not code.upper().startswith('PANTONE'):
            mapping = PantoneColorMap.query.filter_by(pantone_code='PANTONE ' + code).first()
        if not mapping:
            mapping = PantoneColorMap.query.filter(PantoneColorMap.pantone_code.like(f'%{code}%')).first()
        if mapping:
            return api_response(data=mapping.to_dict())
        else:
            return api_response(code=404, message='\u672a\u627e\u5230\u5bf9\u5e94\u8272\u503c')
    except Exception as e:
        return api_response(code=500, message=str(e))

