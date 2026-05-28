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
from app.models.case import MorandiPalette, PantoneColorMap, CaseSpaceMaterial, CaseSlideConfig, SlideTemplate
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
        # 手动解析 bool，避免 Flask type=bool 把空字符串解析为 True
        def parse_bool(val):
            if val is None or val == '': return None
            return val.lower() in ('1', 'true', 'yes')
        is_public = parse_bool(request.args.get('is_public'))
        is_featured = parse_bool(request.args.get('is_featured'))
        
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
        
        # 预算区间筛选 (单位：元)
        price_min = request.args.get('price_min', type=int)
        price_max = request.args.get('price_max', type=int)
        if price_min:
            query = query.filter(CaseStudy.total_price >= price_min)
        if price_max:
            query = query.filter(CaseStudy.total_price <= price_max)

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
            'atmosphere', 'scene_tags', 'responsible_id', 'enable_subscription', 'enable_notify',
            'planner_id', 'designer_id', 'storage_plan', 'execution_detail',
            'is_top', 'top_position'
        ]
        
        for field in fields:
            if field in data:
                setattr(case, field, data[field])
        
                # 处理场景标签：前端发送数组，数据库存储JSON字符串
        if 'scene_tags' in data:
            st_data = data['scene_tags']
            if isinstance(st_data, list):
                case.scene_tags = json.dumps(st_data, ensure_ascii=False)
            elif isinstance(st_data, str):
                case.scene_tags = st_data
            else:
                case.scene_tags = '[]'

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
        
        data = case.to_dict(include_relations=True)
        
        # === V3.2: 追加6阶段内容 + 空间效果图 + 报价信息 ===
        # phases（6个阶段，按编号排序）
        try:
            from app.models.case import CasePhase
            phases = CasePhase.query.filter_by(case_id=id).order_by(CasePhase.phase_number).all()
            phases_dict = {p.phase_number: p.to_dict() for p in phases}
            # 确保返回6个槽位
            data['phases'] = {i: phases_dict.get(i) for i in range(1, 10)}
        except Exception:
            data['phases'] = {i: None for i in range(1, 10)}
        
        # spaces（空间效果图分组）
        try:
            from app.models.case import CaseSpaceRendering
            spaces = CaseSpaceRendering.query.filter_by(case_id=id).order_by(CaseSpaceRendering.sort_order).all()
            data['spaces'] = [s.to_dict() for s in spaces]
        except Exception:
            data['spaces'] = []
        
        # quote 报价简要（总价+分项，由前端拉取完整报价）
        if case.quote_id:
            try:
                from app.models.quote import Quote
                quote = Quote.query.get(case.quote_id)
                if quote:
                    from app.models.quote import QuoteItem
                    quote_items = QuoteItem.query.filter_by(quote_id=quote.id).all()
                    data['quote_info'] = {
                        'id': quote.id,
                        'quote_no': quote.quote_no,
                        'total_amount': float(quote.total_amount) if quote.total_amount else 0,
                        'status': quote.status,
                        'title': quote.title,
                        'items': [i.to_dict() for i in quote_items],
                    }
            except Exception:
                data['quote_info'] = None
        else:
            data['quote_info'] = None
        
        return api_response(data=data)
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



# ============================================================
# V3.2 视觉素材6阶段 API
# ============================================================

@case_bp.route('/cases/<int:id>/phases', methods=['GET'])
@jwt_required_v2
def get_case_phases(current_user, id):
    """获取案例所有阶段内容"""
    try:
        from app.models.case import CasePhase
        phases = CasePhase.query.filter_by(case_id=id).order_by(CasePhase.phase_number).all()
        # 确保返回6个阶段（即使为空）
        result = {i: None for i in range(1, 7)}
        for p in phases:
            result[p.phase_number] = p.to_dict()
        return api_response(data=result)
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/phases/<int:phase_num>', methods=['PUT'])
@jwt_required_v2
def update_case_phase(current_user, id, phase_num):
    """更新指定阶段内容"""
    try:
        from app.models.case import CasePhase
        data = request.get_json()
        
        phase = CasePhase.query.filter_by(case_id=id, phase_number=phase_num).first()
        if not phase:
            phase = CasePhase(case_id=id, phase_number=phase_num)
            db.session.add(phase)
        
        # 阶段名称
        phase_names = {
            1: '户型分析',
            2: '设计意境',
            3: '平面规划',
            4: '鸟瞰展示',
            5: '效果图首页',
            6: '空间效果图',
            7: '材质展示',
            8: '物料展示',
            9: '工法展示'
        }
        phase.phase_name = phase_names.get(phase_num, '')
        
        # 根据阶段号更新对应字段
        if phase_num == 1:
            if 'layout_images' in data:
                phase.layout_images = json.dumps(data['layout_images'])
            if 'layout_analysis' in data:
                phase.layout_analysis = data['layout_analysis']
        elif phase_num == 2:
            if 'mood_images' in data:
                phase.mood_images = json.dumps(data['mood_images'])
            if 'mood_text' in data:
                phase.mood_text = data['mood_text']
        elif phase_num == 3:
            if 'plan_image' in data:
                phase.plan_image = data['plan_image']
            if 'plan_text' in data:
                phase.plan_text = data['plan_text']
        elif phase_num == 4:
            if 'birdview_images' in data:
                phase.birdview_images = json.dumps(data['birdview_images'])
        elif phase_num == 5:
            if 'showcase_images' in data:
                phase.showcase_images = json.dumps(data['showcase_images'])
            if 'showcase_title1' in data:
                phase.showcase_title1 = data['showcase_title1']
            if 'showcase_title2' in data:
                phase.showcase_title2 = data['showcase_title2']
            if 'showcase_text_cn' in data:
                phase.showcase_text_cn = data['showcase_text_cn']
            if 'showcase_text_en' in data:
                phase.showcase_text_en = data['showcase_text_en']
        elif phase_num == 6:
            pass  # 阶段6通过空间效果图API单独管理
        elif phase_num == 7:
            if 'material_gallery' in data:
                phase.material_gallery = json.dumps(data['material_gallery'])
            if 'material_specs' in data:
                phase.material_specs = data['material_specs']
        elif phase_num == 8:
            if 'product_gallery' in data:
                phase.product_gallery = json.dumps(data['product_gallery'])
            if 'product_list' in data:
                phase.product_list = json.dumps(data['product_list'])
        elif phase_num == 9:
            if 'process_gallery' in data:
                phase.process_gallery = json.dumps(data['process_gallery'])
            if 'process_desc' in data:
                phase.process_desc = data['process_desc']
        
        db.session.commit()
        return api_response(data=phase.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ============================================================
# 空间效果图 API (阶段6)
# ============================================================

@case_bp.route('/cases/<int:id>/spaces', methods=['GET'])
@jwt_required_v2
def get_case_spaces(current_user, id):
    """获取案例空间列表"""
    try:
        from app.models.case import CaseSpaceRendering
        spaces = CaseSpaceRendering.query.filter_by(case_id=id).order_by(CaseSpaceRendering.sort_order).all()
        return api_response(data=[s.to_dict() for s in spaces])
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/spaces', methods=['POST'])
@jwt_required_v2
def add_case_space(current_user, id):
    """添加空间"""
    try:
        from app.models.case import CaseSpaceRendering
        data = request.get_json()
        
        # 获取当前最大排序号
        max_order = db.session.query(db.func.max(CaseSpaceRendering.sort_order)).filter_by(case_id=id).scalar() or 0
        
        space = CaseSpaceRendering(
            case_id=id,
            space_name=data.get('space_name', '未命名空间'),
            sort_order=max_order + 1
        )
        db.session.add(space)
        db.session.commit()
        return api_response(data=space.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/<int:space_id>', methods=['PUT'])
@jwt_required_v2
def update_case_space(current_user, space_id):
    """更新空间"""
    try:
        from app.models.case import CaseSpaceRendering
        space = CaseSpaceRendering.query.get(space_id)
        if not space:
            return api_response(code=404, message='空间不存在')
        
        data = request.get_json()
        if 'space_name' in data:
            space.space_name = data['space_name']
        if 'sort_order' in data:
            space.sort_order = data['sort_order']
        
        db.session.commit()
        return api_response(data=space.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/<int:space_id>', methods=['DELETE'])
@jwt_required_v2
def delete_case_space(current_user, space_id):
    """删除空间（级联删除效果图）"""
    try:
        from app.models.case import CaseSpaceRendering
        space = CaseSpaceRendering.query.get(space_id)
        if not space:
            return api_response(code=404, message='空间不存在')
        
        db.session.delete(space)
        db.session.commit()
        return api_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ============================================================
# 效果图 API
# ============================================================

@case_bp.route('/spaces/<int:space_id>/renderings', methods=['GET'])
@jwt_required_v2
def get_space_renderings(current_user, space_id):
    """获取空间下的效果图列表"""
    try:
        from app.models.case import CaseRenderingItem
        items = CaseRenderingItem.query.filter_by(space_id=space_id).order_by(CaseRenderingItem.sort_order).all()
        return api_response(data=[i.to_dict() for i in items])
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/<int:space_id>/renderings', methods=['POST'])
@jwt_required_v2
def add_space_rendering(current_user, space_id):
    """添加效果图"""
    try:
        from app.models.case import CaseRenderingItem
        data = request.get_json()
        
        # 获取当前最大排序号
        max_order = db.session.query(db.func.max(CaseRenderingItem.sort_order)).filter_by(space_id=space_id).scalar() or 0
        
        item = CaseRenderingItem(
            space_id=space_id,
            image_url=data.get('image_url', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            sort_order=max_order + 1
        )
        db.session.add(item)
        db.session.commit()
        return api_response(data=item.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/renderings/<int:rendering_id>', methods=['PUT'])
@jwt_required_v2
def update_rendering(current_user, rendering_id):
    """更新效果图"""
    try:
        from app.models.case import CaseRenderingItem
        item = CaseRenderingItem.query.get(rendering_id)
        if not item:
            return api_response(code=404, message='效果图不存在')
        
        data = request.get_json()
        if 'image_url' in data:
            item.image_url = data['image_url']
        if 'title' in data:
            item.title = data['title']
        if 'description' in data:
            item.description = data['description']
        if 'sort_order' in data:
            item.sort_order = data['sort_order']
        
        db.session.commit()
        return api_response(data=item.to_dict())
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/renderings/<int:rendering_id>', methods=['DELETE'])
@jwt_required_v2
def delete_rendering(current_user, rendering_id):
    """删除效果图"""
    try:
        from app.models.case import CaseRenderingItem
        item = CaseRenderingItem.query.get(rendering_id)
        if not item:
            return api_response(code=404, message='效果图不存在')
        
        db.session.delete(item)
        db.session.commit()
        return api_response(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))



@case_bp.route('/cases/budget-stats', methods=['GET'])
def get_budget_stats():
    """获取预算分布统计（公开接口，供前台案例列表使用）"""
    try:
        from app.models.case import CaseStudy

        rows = db.session.query(
            CaseStudy.total_price
        ).filter(
            CaseStudy.status == '已发布',
            CaseStudy.deleted_at.is_(None),
            CaseStudy.total_price.isnot(None),
            CaseStudy.total_price > 0
        ).all()

        prices = [r[0] for r in rows if r[0]]
        if not prices:
            return api_response(data={'min_wan': 10, 'max_wan': 100, 'buckets': [], 'total': 0})

        min_price = min(prices)
        max_price = max(prices)

        # 构建直方图桶（每10万一档）
        bucket_size = 100000
        buckets = []
        current = int(min_price // bucket_size) * bucket_size
        max_buckets = 15

        while current <= max_price + bucket_size and len(buckets) < max_buckets:
            bucket_start = current
            next_val = current + bucket_size

            if current < 100000:
                label = f'{current//10000}万以下'
            elif next_val > max_price:
                label = f'{current//10000}万+'
            else:
                label = f'{current//10000}-{next_val//10000}万'

            count = sum(1 for p in prices if bucket_start <= p < next_val)
            if next_val > max_price:
                count = sum(1 for p in prices if bucket_start <= p)

            buckets.append({'label': label, 'count': count, 'mid': current})
            current += bucket_size

        return api_response(data={
            'min_wan': round(min_price / 10000, 1),
            'max_wan': round(max_price / 10000, 1),
            'min': min_price,
            'max': max_price,
            'buckets': buckets,
            'total': len(prices)
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/public', methods=['GET'])
def list_public_cases():
    """公开案例列表（无需认证，支持预算区间筛选）"""
    try:
        from app.models.case import CaseStudy
        from sqlalchemy import or_

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 12, type=int)
        is_featured = request.args.get('is_featured')
        atmosphere = request.args.get('atmosphere')
        workflow_phase = request.args.get('workflow_phase')
        color = request.args.get('color')
        price_min = request.args.get('price_min', type=int)
        price_max = request.args.get('price_max', type=int)
        keyword = request.args.get('keyword')

        query = CaseStudy.query.filter(
            CaseStudy.status == '已发布',
            CaseStudy.deleted_at.is_(None)
        )

        if is_featured and is_featured not in ['', 'all']:
            if is_featured.lower() == 'true':
                query = query.filter(CaseStudy.is_featured == True)
            elif is_featured.lower() == 'false':
                query = query.filter(CaseStudy.is_featured == False)

        if atmosphere:
            query = query.filter(CaseStudy.atmosphere == atmosphere)

        if workflow_phase:
            query = query.filter(CaseStudy.workflow_phase == workflow_phase)

        if color:
            query = query.filter(or_(
                CaseStudy.main_colors.contains(color),
                CaseStudy.auxiliary_colors.contains(color),
                CaseStudy.accent_colors.contains(color),
                CaseStudy.background_colors.contains(color)
            ))

        if price_min:
            query = query.filter(CaseStudy.total_price >= price_min)
        if price_max:
            query = query.filter(CaseStudy.total_price <= price_max)

        if keyword:
            query = query.filter(or_(
                CaseStudy.title.contains(keyword),
                CaseStudy.subtitle.contains(keyword),
                CaseStudy.building_name.contains(keyword),
                CaseStudy.design_style.contains(keyword)
            ))

        total = query.count()
        items = query.order_by(
            CaseStudy.is_featured.desc(),
            CaseStudy.sort_order.desc(),
            CaseStudy.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()

        return api_response(items=[c.to_dict() for c in items], total=total, page=page, pageSize=page_size)
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/reorder', methods=['POST'])
@jwt_required_v2
def reorder_spaces(current_user):
    """批量重排空间顺序"""
    try:
        from app.models.case import CaseSpaceRendering
        data = request.get_json()
        orders = data.get('orders', [])  # [{id: 1, sort_order: 1}, ...]
        
        for item in orders:
            space = CaseSpaceRendering.query.get(item['id'])
            if space:
                space.sort_order = item['sort_order']
        
        db.session.commit()
        return api_response(message='排序成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ==================== V3.3 幻灯片演示 + 空间物料配置 ====================


@case_bp.route('/cases/<int:id>/slide-config', methods=['GET'])
@jwt_required_v2
def get_slide_config(current_user, id):
    """获取案例幻灯片配置"""
    try:
        config = CaseSlideConfig.query.filter_by(case_id=id).first()
        if not config:
            # 自动创建默认配置，自动关联模板
            case = CaseStudy.query.get(id)
            config = CaseSlideConfig(case_id=id, template_id=case.slide_template_id if case else None)
            db.session.add(config)
            db.session.commit()
        return api_response(data=config.to_dict())
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/slide-config', methods=['PUT'])
@jwt_required_v2
def update_slide_config(current_user, id):
    """更新案例幻灯片配置"""
    try:
        config = CaseSlideConfig.query.filter_by(case_id=id).first()
        if not config:
            config = CaseSlideConfig(case_id=id)
            db.session.add(config)

        data = request.get_json()
        for field in ['template_id', 'template_style', 'primary_color', 'aspect_ratio',
                       'cover_title', 'cover_subtitle', 'cover_bg_image',
                       'inner_bg_image', 'back_bg_image',
                       'about_title', 'about_content', 'about_image', 'about_subtitle',
                       'show_about', 'show_team', 'show_toc', 'show_material',
                       'show_product', 'show_process', 'show_summary']:
            if field in data:
                setattr(config, field, data[field])

        db.session.commit()
        return api_response(data=config.to_dict(), message='幻灯片配置已更新')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/slide-data', methods=['GET'])
@jwt_required_v2
def get_slide_data(current_user, id):
    """获取案例幻灯片完整数据（用于前端渲染）"""
    try:
        from app.models.case import CasePhase, CaseSpaceRendering, CaseRenderingItem
        from app.models.frontend_config import PageConfig
        from app.models.hr import Employee

        case = CaseStudy.query.get(id)
        if not case:
            return api_response(code=404, message='案例不存在')

        case_data = case.to_dict(include_relations=True)

        # 获取幻灯片配置
        config = CaseSlideConfig.query.filter_by(case_id=id).first()
        if config:
            slide_config = config.to_dict()
        else:
            # 未创建配置时返回默认值，自动关联模板
            slide_config = {
                'id': None, 'case_id': id,
                'template_id': case.slide_template_id if case.slide_template_id else None,
                'template_style': 'dark', 'primary_color': '#8B4513',
                'aspect_ratio': '16:9',
                'cover_title': None, 'cover_subtitle': None, 'cover_bg_image': None,
                'inner_bg_image': None, 'back_bg_image': None,
                'about_title': '关于我们', 'about_content': None, 'about_image': None, 'about_subtitle': None,
                'show_about': True, 'show_team': True, 'show_toc': True,
                'show_material': True, 'show_product': True, 'show_process': True, 'show_summary': True,
                'created_at': None, 'updated_at': None,
            }

        phases = CasePhase.query.filter_by(case_id=id).order_by(CasePhase.phase_number).all()
        phases_data = {p.phase_number: p.to_dict() for p in phases}

        spaces = CaseSpaceRendering.query.filter_by(case_id=id).order_by(CaseSpaceRendering.sort_order).all()
        spaces_data = [s.to_dict(include_items=True) for s in spaces]

        # 获取空间物料配置
        materials = CaseSpaceMaterial.query.filter_by(case_id=id).order_by(
            CaseSpaceMaterial.space_name, CaseSpaceMaterial.category_level1, CaseSpaceMaterial.sort_order
        ).all()
        materials_data = [m.to_dict() for m in materials]

        # 如果案例没有物料配置，从物料库(MaterialSKU)读取作为备选数据
        if not materials_data:
            from app.models.material_sku import MaterialSKU, MaterialCategory
            skus = MaterialSKU.query.filter_by(is_deleted=False).order_by(
                MaterialSKU.category_id, MaterialSKU.sort_order
            ).all()
            # 构建分类映射
            cat_map = {}
            all_cats = MaterialCategory.query.filter_by(is_deleted=False).all()
            for c in all_cats:
                cat_map[c.id] = c.name
                if c.parent_id:
                    cat_map[str(c.id) + '_parent'] = c.parent_id
            for sku in skus:
                cat1_name = ''
                cat2_name = cat_map.get(sku.category_id, '')
                parent_id = cat_map.get(str(sku.category_id) + '_parent')
                if parent_id:
                    cat1_name = cat_map.get(parent_id, '')
                materials_data.append({
                    'id': sku.id,
                    'space_id': None,
                    'case_id': id,
                    'sku_id': sku.id,
                    'sku_code': sku.sku_code,
                    'material_name': sku.name,
                    'material_image': sku.main_image,
                    'material': sku.material or '',
                    'custom_name': '',
                    'custom_measure': '',
                    'sku_name': sku.name,
                    'category_level1': cat1_name,
                    'category_level2': cat2_name,
                    'brand': sku.brand or '',
                    'spec': sku.specification or '',
                    'unit': sku.unit or '',
                    'quantity': 1,
                    'unit_price': float(sku.sale_price) if sku.sale_price else 0,
                    'total_price': float(sku.sale_price) if sku.sale_price else 0,
                    'env_level': sku.env_level or '合格',
                    'supply_chain': sku.supply_chain or '直供',
                    'color_name': sku.color_name or '',
                    'width': None,
                    'depth': None,
                    'height': None,
                })

        # 按一级+二级分类聚合物料汇总
        material_summary = {}
        for m in materials_data:
            l1 = m.get('category_level1') or '其他'
            l2 = m.get('category_level2') or ''
            cat_label = f"{l1}-{l2}" if l2 else l1
            if cat_label not in material_summary:
                material_summary[cat_label] = {
                    'category': cat_label,
                    'l1': l1,
                    'l2': l2,
                    'measure_total': 0,
                    'measure_unit': '',
                    'total': 0
                }
            ms = float(m.get('custom_measure') or 0)
            if ms > 0:
                material_summary[cat_label]['measure_total'] += ms
                material_summary[cat_label]['measure_unit'] = m.get('unit') or '㎡'
            material_summary[cat_label]['total'] += float(m.get('total_price', 0) or 0)


        # 获取页面配置中的关于我们信息（系统设置）
        page_about = {}
        home_config = PageConfig.query.filter_by(page_key='home').first()
        if home_config and home_config.sections:
            for section in home_config.sections:
                if section.get('component') == 'AboutSection':
                    cfg = section.get('config', {})
                    page_about = {
                        'title': cfg.get('title', ''),
                        'content': cfg.get('content', ''),
                        'highlights': cfg.get('highlights', []),
                    }
                    break

        # 获取设计团队员工数据
        team_members = []
        designers = Employee.query.filter_by(is_deleted=False, department_id=2).all()
        for emp in designers:
            if emp.title:  # 只展示有职称的员工
                team_members.append({
                    'id': emp.id,
                    'name': emp.name,
                    'title': emp.title,
                    'avatar': emp.avatar,
                    'showcase_photo': emp.showcase_photo,
                    'bio': emp.bio,
                    'department_name': emp.department.name if emp.department else None,
                })

        # 获取材质展示选中物料
        showcase_materials = []
        if config and config.showcase_material_ids:
            from app.models.material_sku import MaterialSKU as _SKU, MaterialCategory as _MC
            for sid in config.showcase_material_ids:
                sku = _SKU.query.filter_by(id=sid, is_deleted=False).first()
                if sku and sku.main_image:
                    # 获取L1/L2名称
                    l2_name = sku.category.name if sku.category else ''
                    l1_name = ''
                    if sku.category and sku.category.parent_id:
                        parent = _MC.query.get(sku.category.parent_id)
                        l1_name = parent.name if parent else ''
                    showcase_materials.append({
                        'sku_id': sku.id,
                        'sku_name': sku.name,
                        'main_image': sku.main_image,
                        'spec': sku.specification or '',
                        'brand': sku.brand or '',
                        'l1': l1_name,
                        'l2': l2_name,
                    })

        return api_response(data={
            'case': case_data,
            'slide_config': slide_config,
            'phases': phases_data,
            'spaces': spaces_data,
            'materials': materials_data,
            'material_summary': list(material_summary.values()),
            'page_about': page_about,
            'team_members': team_members,
            'showcase_materials': showcase_materials,
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


# ===== 空间物料配置 CRUD =====

@case_bp.route('/cases/<int:id>/space-materials', methods=['GET'])
@jwt_required_v2
def get_space_materials(current_user, id):
    """获取案例所有空间物料配置"""
    try:
        materials = CaseSpaceMaterial.query.filter_by(case_id=id).order_by(
            CaseSpaceMaterial.space_name, CaseSpaceMaterial.sort_order
        ).all()
        return api_response(data=[m.to_dict() for m in materials])
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/<int:space_id>/materials', methods=['GET'])
@jwt_required_v2
def get_space_materials_by_space(current_user, space_id):
    """获取某空间的物料配置"""
    try:
        materials = CaseSpaceMaterial.query.filter_by(space_id=space_id).order_by(
            CaseSpaceMaterial.sort_order
        ).all()
        return api_response(data=[m.to_dict() for m in materials])
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/<int:space_id>/materials', methods=['POST'])
@jwt_required_v2
def add_space_material(current_user, space_id):
    """给空间添加物料配置"""
    try:
        from app.models.case import CaseSpaceRendering
        space = CaseSpaceRendering.query.get(space_id)
        if not space:
            return api_response(code=404, message='空间不存在')

        data = request.get_json()
        material = CaseSpaceMaterial(
            space_id=space_id,
            case_id=space.case_id,
            space_name=data.get('space_name', space.space_name),
            room_name=data.get('room_name'),
            sku_id=data.get('sku_id'),
            sku_code=data.get('sku_code'),
            material_name=data.get('material_name'),
            material_image=data.get('material_image'),
            category_level1=data.get('category_level1'),
            category_level2=data.get('category_level2'),
            category_level3=data.get('category_level3'),
            brand=data.get('brand'),
            spec=data.get('spec'),
            unit=data.get('unit'),
            quantity=data.get('quantity', 1),
            unit_price=data.get('unit_price', 0),
            total_price=data.get('total_price', 0),
            sort_order=data.get('sort_order', 0),
        )
        db.session.add(material)
        db.session.commit()
        return api_response(data=material.to_dict(), message='物料配置已添加')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/spaces/<int:space_id>/full', methods=['PUT'])
@jwt_required_v2
def save_space_materials_full(current_user, space_id):
    """保存空间物料配置（全量替换）"""
    try:
        from app.models.case import CaseSpaceRendering
        space = CaseSpaceRendering.query.get(space_id)
        if not space:
            return api_response(code=404, message='空间不存在')

        data = request.get_json()
        configs = data.get('configs', [])

        # 删除该空间原有物料配置
        CaseSpaceMaterial.query.filter_by(space_id=space_id).delete()

        # 批量写入新配置
        for idx, c in enumerate(configs):
            material = CaseSpaceMaterial(
                space_id=space_id,
                case_id=space.case_id,
                space_name=space.space_name,
                sku_id=c.get('material_id'),
                sku_code=c.get('sku_code'),
                material_name=c.get('name') or c.get('material_name'),
                material_image=c.get('main_image'),
                category_level1=c.get('category_level1'),
                category_level2=c.get('category_level2'),
                category_level3=c.get('category_level3'),
                brand=c.get('brand'),
                spec=c.get('spec'),
                unit=c.get('unit'),
                env_level=c.get('env_level'),
                supply_chain=c.get('supply_chain'),
                color_name=c.get('color_name'),
                custom_name=c.get('custom_name'),
                material=c.get('material'),
                custom_measure=c.get('custom_measure'),
                width=float(c['width']) if c.get('width') else None,
                depth=float(c['depth']) if c.get('depth') else None,
                height=float(c['height']) if c.get('height') else None,
                quantity=float(c.get('quantity', 1) or 1),
                unit_price=float(c.get('price', 0) or 0),
                total_price=float(c.get('amount', 0) or 0),
                sort_order=idx,
            )
            db.session.add(material)

        db.session.commit()
        return api_response(message='物料配置已保存')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/space-materials/<int:material_id>', methods=['PUT'])
@jwt_required_v2
def update_space_material(current_user, material_id):
    """更新空间物料配置"""
    try:
        material = CaseSpaceMaterial.query.get(material_id)
        if not material:
            return api_response(code=404, message='物料配置不存在')

        data = request.get_json()
        for field in ['space_name', 'room_name', 'sku_id', 'sku_code', 'material_name',
                       'material_image', 'category_level1', 'category_level2', 'category_level3',
                       'brand', 'spec', 'unit', 'env_level', 'supply_chain', 'color_name',
                       'custom_name', 'material', 'custom_measure', 'width', 'depth', 'height',
                       'quantity', 'unit_price', 'total_price', 'sort_order']:
            if field in data:
                setattr(material, field, data[field])

        db.session.commit()
        return api_response(data=material.to_dict(), message='物料配置已更新')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/space-materials/<int:material_id>', methods=['DELETE'])
@jwt_required_v2
def delete_space_material(current_user, material_id):
    """删除空间物料配置"""
    try:
        material = CaseSpaceMaterial.query.get(material_id)
        if not material:
            return api_response(code=404, message='物料配置不存在')

        db.session.delete(material)
        db.session.commit()
        return api_response(message='物料配置已删除')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/space-materials/batch', methods=['POST'])
@jwt_required_v2
def batch_import_materials(current_user, id):
    """批量导入物料配置（从报价单导入）"""
    try:
        from app.models.quote import QuoteItem
        data = request.get_json()
        quote_id = data.get('quote_id')

        if not quote_id:
            return api_response(code=400, message='请指定报价单ID')

        # 获取该案例的空间列表
        from app.models.case import CaseSpaceRendering
        spaces = CaseSpaceRendering.query.filter_by(case_id=id).all()
        space_map = {s.space_name: s for s in spaces}

        # 获取报价单物料
        quote_items = QuoteItem.query.filter_by(quote_id=quote_id).all()

        added = 0
        for item in quote_items:
            # 按空间名匹配
            space = space_map.get(item.space_name)
            if not space:
                continue

            material = CaseSpaceMaterial(
                space_id=space.id,
                case_id=id,
                space_name=item.space_name or space.space_name,
                room_name=item.room_name,
                sku_id=item.sku_id,
                sku_code=item.sku_code,
                material_name=item.material_name or item.name,
                material_image=item.material_image,
                category_level1=item.category_level1,
                category_level2=item.category_level2,
                category_level3=item.category_level3,
                brand=item.brand,
                spec=item.spec,
                unit=item.unit,
                quantity=float(item.quantity) if item.quantity else 1,
                unit_price=float(item.unit_price) if item.unit_price else 0,
                total_price=float(item.total_price) if item.total_price else 0,
            )
            db.session.add(material)
            added += 1

        db.session.commit()
        return api_response(data={'added': added}, message=f'成功导入{added}条物料配置')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/public/cases/<int:id>/slide-data', methods=['GET'])
def get_public_slide_data(id):
    """公开接口：获取案例幻灯片数据"""
    try:
        from app.models.case import CasePhase, CaseSpaceRendering
        from app.models.frontend_config import PageConfig
        from app.models.hr import Employee

        case = CaseStudy.query.get(id)
        if not case:
            return api_response(code=404, message='案例不存在')
        if not case.is_public:
            return api_response(code=403, message='该案例未公开')

        case_data = case.to_dict(include_relations=True)

        config = CaseSlideConfig.query.filter_by(case_id=id).first()
        if config:
            slide_config = config.to_dict()
        else:
            slide_config = {
                'id': None, 'case_id': id,
                'template_id': case.slide_template_id if case.slide_template_id else None,
                'template_style': 'dark', 'primary_color': '#8B4513',
                'aspect_ratio': '16:9',
                'cover_title': None, 'cover_subtitle': None, 'cover_bg_image': None,
                'inner_bg_image': None, 'back_bg_image': None,
                'about_title': '关于我们', 'about_content': None, 'about_image': None, 'about_subtitle': None,
                'show_about': True, 'show_team': True, 'show_toc': True,
                'show_material': True, 'show_product': True, 'show_process': True, 'show_summary': True,
                'created_at': None, 'updated_at': None,
            }

        # Apply template fallback: null config fields inherit from template
        # This implements "default to public template" + personalized override
        template_id = slide_config.get('template_id')
        if not template_id:
            template_id = case.slide_template_id
        if template_id:
            template = SlideTemplate.query.get(template_id)
            if template:
                tpl_dict = template.to_dict()
                # For each template field: if slide_config value is None, use template value
                for key, val in tpl_dict.items():
                    if slide_config.get(key) is None and val is not None:
                        slide_config[key] = val

        phases = CasePhase.query.filter_by(case_id=id).order_by(CasePhase.phase_number).all()
        phases_data = {p.phase_number: p.to_dict() for p in phases}

        spaces = CaseSpaceRendering.query.filter_by(case_id=id).order_by(CaseSpaceRendering.sort_order).all()
        spaces_data = [s.to_dict(include_items=True) for s in spaces]

        materials = CaseSpaceMaterial.query.filter_by(case_id=id).order_by(
            CaseSpaceMaterial.space_name, CaseSpaceMaterial.category_level1, CaseSpaceMaterial.sort_order
        ).all()
        materials_data = [m.to_dict() for m in materials]

        # 如果案例没有物料配置，从物料库(MaterialSKU)读取作为备选数据
        if not materials_data:
            from app.models.material_sku import MaterialSKU, MaterialCategory
            skus = MaterialSKU.query.filter_by(is_deleted=False).order_by(
                MaterialSKU.category_id, MaterialSKU.sort_order
            ).all()
            cat_map = {}
            all_cats = MaterialCategory.query.filter_by(is_deleted=False).all()
            for c in all_cats:
                cat_map[c.id] = c.name
                if c.parent_id:
                    cat_map[str(c.id) + '_parent'] = c.parent_id
            for sku in skus:
                cat1_name = ''
                cat2_name = cat_map.get(sku.category_id, '')
                parent_id = cat_map.get(str(sku.category_id) + '_parent')
                if parent_id:
                    cat1_name = cat_map.get(parent_id, '')
                materials_data.append({
                    'id': sku.id,
                    'space_id': None,
                    'case_id': id,
                    'sku_id': sku.id,
                    'sku_code': sku.sku_code,
                    'material_name': sku.name,
                    'material_image': sku.main_image,
                    'material': sku.material or '',
                    'custom_name': '',
                    'custom_measure': '',
                    'sku_name': sku.name,
                    'category_level1': cat1_name,
                    'category_level2': cat2_name,
                    'brand': sku.brand or '',
                    'spec': sku.specification or '',
                    'unit': sku.unit or '',
                    'quantity': 1,
                    'unit_price': float(sku.sale_price) if sku.sale_price else 0,
                    'total_price': float(sku.sale_price) if sku.sale_price else 0,
                    'env_level': sku.env_level or '合格',
                    'supply_chain': sku.supply_chain or '直供',
                    'color_name': sku.color_name or '',
                    'width': None,
                    'depth': None,
                    'height': None,
                })

        # 按一级+二级分类聚合物料汇总
        material_summary = {}
        for m in materials_data:
            md = m if isinstance(m, dict) else m.to_dict()
            l1 = md.get('category_level1') or '其他'
            l2 = md.get('category_level2') or ''
            cat_label = f"{l1}-{l2}" if l2 else l1
            if cat_label not in material_summary:
                material_summary[cat_label] = {
                    'category': cat_label,
                    'l1': l1,
                    'l2': l2,
                    'measure_total': 0,
                    'measure_unit': '',
                    'total': 0
                }
            ms = float(md.get('custom_measure') or 0)
            if ms > 0:
                material_summary[cat_label]['measure_total'] += ms
                material_summary[cat_label]['measure_unit'] = md.get('unit') or '㎡'
            material_summary[cat_label]['total'] += float(md.get('total_price', 0) if isinstance(m, dict) else (m.total_price or 0))


        # 获取页面配置中的关于我们信息（系统设置）
        page_about = {}
        home_config = PageConfig.query.filter_by(page_key='home').first()
        if home_config and home_config.sections:
            for section in home_config.sections:
                if section.get('component') == 'AboutSection':
                    cfg = section.get('config', {})
                    page_about = {
                        'title': cfg.get('title', ''),
                        'content': cfg.get('content', ''),
                        'highlights': cfg.get('highlights', []),
                    }
                    break

        # 获取设计团队员工数据
        team_members = []
        designers = Employee.query.filter_by(is_deleted=False, department_id=2).all()
        for emp in designers:
            if emp.title:  # 只展示有职称的员工
                team_members.append({
                    'id': emp.id,
                    'name': emp.name,
                    'title': emp.title,
                    'avatar': emp.avatar,
                    'showcase_photo': emp.showcase_photo,
                    'bio': emp.bio,
                    'department_name': emp.department.name if emp.department else None,
                })

        # 获取材质展示选中物料
        showcase_materials = []
        if config and config.showcase_material_ids:
            from app.models.material_sku import MaterialSKU as _SKU2, MaterialCategory as _MC2
            for sid in config.showcase_material_ids:
                sku = _SKU2.query.filter_by(id=sid, is_deleted=False).first()
                if sku and sku.main_image:
                    l2_name = sku.category.name if sku.category else ''
                    l1_name = ''
                    if sku.category and sku.category.parent_id:
                        parent = _MC2.query.get(sku.category.parent_id)
                        l1_name = parent.name if parent else ''
                    showcase_materials.append({
                        'sku_id': sku.id,
                        'sku_name': sku.name,
                        'main_image': sku.main_image,
                        'spec': sku.specification or '',
                        'brand': sku.brand or '',
                        'l1': l1_name,
                        'l2': l2_name,
                    })

        return api_response(data={
            'case': case_data,
            'slide_config': slide_config,
            'phases': phases_data,
            'spaces': spaces_data,
            'materials': materials_data,
            'material_summary': list(material_summary.values()),
            'page_about': page_about,
            'team_members': team_members,
            'showcase_materials': showcase_materials,
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


# ===== 材质展示（阶段7） =====

# 收集候选物料的L2分类ID：固装家具-柜体投影/柜门，硬装主材-地面/墙面，软装饰品-布艺软装
SHOWCASE_L2_IDS = [26, 27, 10, 11, 44]  # 柜体投影, 柜门, 地面主材, 墙面/顶面主材, 布艺软装


@case_bp.route('/cases/<int:id>/showcase-candidates', methods=['GET'])
@jwt_required_v2
def get_showcase_candidates(current_user, id):
    """获取案例材质展示候选物料（去重）"""
    try:
        from app.models.material_sku import MaterialSKU, MaterialCategory

        case = CaseStudy.query.get(id)
        if not case:
            return api_response(code=404, message='案例不存在')

        # 从案例物料配置中收集有sku_id的记录，按sku_id去重
        materials = CaseSpaceMaterial.query.filter_by(case_id=id).all()
        seen_sku_ids = set()
        candidates = []

        # 构建分类映射
        cat_map = {}
        all_cats = MaterialCategory.query.filter_by(is_deleted=False).all()
        for c in all_cats:
            cat_map[c.id] = {'name': c.name, 'parent_id': c.parent_id}

        for m in materials:
            if not m.sku_id or m.sku_id in seen_sku_ids:
                continue
            # 检查L2分类是否在收集范围
            sku = MaterialSKU.query.filter_by(id=m.sku_id, is_deleted=False).first()
            if not sku or not sku.main_image:
                continue
            cat_info = cat_map.get(sku.category_id)
            if not cat_info:
                continue
            # 判断是否在SHOWCASE_L2_IDS范围内
            if sku.category_id not in SHOWCASE_L2_IDS:
                # 也检查parent_id对应的L1
                continue
            seen_sku_ids.add(m.sku_id)
            # 获取L1名称
            l2_name = cat_info['name']
            l1_name = ''
            if cat_info['parent_id'] and cat_info['parent_id'] in cat_map:
                l1_name = cat_map[cat_info['parent_id']]['name']
            candidates.append({
                'sku_id': sku.id,
                'sku_name': sku.name,
                'main_image': sku.main_image,
                'spec': sku.specification or '',
                'brand': sku.brand or '',
                'l1': l1_name,
                'l2': l2_name,
            })

        # 获取当前已选中的ID列表
        config = CaseSlideConfig.query.filter_by(case_id=id).first()
        selected_ids = config.showcase_material_ids if config and config.showcase_material_ids else []

        return api_response(data={
            'candidates': candidates,
            'selected_ids': selected_ids,
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/cases/<int:id>/showcase-materials', methods=['POST'])
@jwt_required_v2
def save_showcase_materials(current_user, id):
    """保存案例材质展示选中的SKU ID列表"""
    try:
        case = CaseStudy.query.get(id)
        if not case:
            return api_response(code=404, message='案例不存在')

        data = request.get_json()
        selected_ids = data.get('selected_ids', [])

        config = CaseSlideConfig.query.filter_by(case_id=id).first()
        if not config:
            config = CaseSlideConfig(case_id=id)
            db.session.add(config)
        config.showcase_material_ids = selected_ids
        db.session.commit()
        return api_response(data=config.to_dict(), message='材质展示配置已保存')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


# ==================== V3.4 幻灯片模板管理 ====================


@case_bp.route('/slide-templates', methods=['GET'])
@jwt_required_v2
def list_slide_templates(current_user):
    """获取幻灯片模板列表"""
    try:
        templates = SlideTemplate.query.order_by(SlideTemplate.is_default.desc(), SlideTemplate.id).all()
        return api_response(data=[t.to_dict() for t in templates])
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/slide-templates/<int:template_id>', methods=['GET'])
@jwt_required_v2
def get_slide_template(current_user, template_id):
    """获取单个幻灯片模板"""
    try:
        template = SlideTemplate.query.get(template_id)
        if not template:
            return api_response(code=404, message='模板不存在')
        return api_response(data=template.to_dict())
    except Exception as e:
        return api_response(code=500, message=str(e))


@case_bp.route('/slide-templates', methods=['POST'])
@jwt_required_v2
def create_slide_template(current_user):
    """创建幻灯片模板"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        if not name:
            return api_response(code=400, message='模板名称不能为空')

        existing = SlideTemplate.query.filter_by(name=name).first()
        if existing:
            return api_response(code=400, message=f'模板名称"{name}"已存在')

        template = SlideTemplate(
            name=name,
            description=data.get('description', ''),
            template_style=data.get('template_style', 'dark'),
            primary_color=data.get('primary_color', '#8B4513'),
            aspect_ratio=data.get('aspect_ratio', '16:9'),
            cover_title=data.get('cover_title', ''),
            cover_subtitle=data.get('cover_subtitle', ''),
            brand_name=data.get('brand_name', 'DESIGNARY'),
            cover_bg_image=data.get('cover_bg_image', ''),
            inner_bg_image=data.get('inner_bg_image', ''),
            back_bg_image=data.get('back_bg_image', ''),
            about_title=data.get('about_title', '关于我们'),
            about_subtitle=data.get('about_subtitle', ''),
            about_content=data.get('about_content', ''),
            about_image=data.get('about_image', ''),
            show_about=data.get('show_about', True),
            show_team=data.get('show_team', True),
            show_toc=data.get('show_toc', True),
            show_material=data.get('show_material', True),
            show_product=data.get('show_product', True),
            show_process=data.get('show_process', True),
            show_summary=data.get('show_summary', True),
            is_default=data.get('is_default', False),
            is_active=data.get('is_active', True),
        )
        db.session.add(template)
        db.session.commit()
        return api_response(data=template.to_dict(), message='模板创建成功')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/slide-templates/<int:template_id>', methods=['PUT'])
@jwt_required_v2
def update_slide_template(current_user, template_id):
    """更新幻灯片模板"""
    try:
        template = SlideTemplate.query.get(template_id)
        if not template:
            return api_response(code=404, message='模板不存在')

        data = request.get_json()

        name = data.get('name', '').strip()
        if name and name != template.name:
            existing = SlideTemplate.query.filter(
                SlideTemplate.name == name,
                SlideTemplate.id != template_id
            ).first()
            if existing:
                return api_response(code=400, message=f'模板名称"{name}"已被其他模板使用')

        for field in ['name', 'description', 'template_style', 'primary_color',
                       'aspect_ratio', 'cover_title', 'cover_subtitle', 'brand_name',
                       'cover_bg_image', 'inner_bg_image', 'back_bg_image',
                       'about_title', 'about_subtitle', 'about_content',
                       'about_image', 'show_about', 'show_team', 'show_toc',
                       'show_material', 'show_product', 'show_process',
                       'show_summary', 'is_default', 'is_active']:
            if field in data:
                setattr(template, field, data[field])

        db.session.commit()
        return api_response(data=template.to_dict(), message='模板已更新')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/slide-templates/<int:template_id>', methods=['DELETE'])
@jwt_required_v2
def delete_slide_template(current_user, template_id):
    """删除幻灯片模板"""
    try:
        template = SlideTemplate.query.get(template_id)
        if not template:
            return api_response(code=404, message='模板不存在')

        referenced_count = CaseStudy.query.filter(
            CaseStudy.slide_template_id == template_id,
            CaseStudy.deleted_at == None
        ).count()

        if referenced_count > 0:
            return api_response(code=400, message=f'该模板已被 {referenced_count} 个案例使用，请先解除引用再删除')

        db.session.delete(template)
        db.session.commit()
        return api_response(message='模板已删除')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))


@case_bp.route('/slide-templates/<int:template_id>/duplicate', methods=['POST'])
@jwt_required_v2
def duplicate_slide_template(current_user, template_id):
    """复制幻灯片模板"""
    try:
        data = request.get_json() or {}
        source = SlideTemplate.query.get(template_id)
        if not source:
            return api_response(code=404, message='模板不存在')

        new_name = data.get('name', f'{source.name} (副本)').strip()
        base_name = new_name
        counter = 1
        while SlideTemplate.query.filter_by(name=new_name).first():
            new_name = f'{base_name} ({counter})'
            counter += 1

        clone = SlideTemplate(
            name=new_name,
            description=source.description,
            template_style=source.template_style,
            primary_color=source.primary_color,
            aspect_ratio=source.aspect_ratio,
            cover_title=source.cover_title,
            cover_subtitle=source.cover_subtitle,
            cover_bg_image=source.cover_bg_image,
            inner_bg_image=source.inner_bg_image,
            back_bg_image=source.back_bg_image,
            about_title=source.about_title,
            about_subtitle=source.about_subtitle,
            about_content=source.about_content,
            about_image=source.about_image,
            show_about=source.show_about,
            show_team=source.show_team,
            show_toc=source.show_toc,
            show_material=source.show_material,
            show_product=source.show_product,
            show_process=source.show_process,
            show_summary=source.show_summary,
            is_default=False,
            is_active=True,
        )
        db.session.add(clone)
        db.session.commit()
        return api_response(data=clone.to_dict(), message='模板已复制')
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=str(e))
