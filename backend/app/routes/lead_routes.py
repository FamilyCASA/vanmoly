"""
留资引导模块路由
API端点: /api/v3/leads
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, asc, or_
from datetime import datetime
from app import db
from app.models.lead_v2 import Lead, LeadFollow


lead_bp = Blueprint('lead', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


@lead_bp.route('/leads', methods=['POST'])
def create_lead():
    """
    提交留资（对外接口，无需登录）
    
    请求体:
    {
        "name": "张先生",
        "phone": "13800138000",
        "source": "案例留资",
        "source_id": 1,
        "source_page": "/cases/1",
        "intention": "想装修新房",
        "budget": "20-30万",
        "house_type": "三室两厅",
        "area": "120"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return api_response(code=400, message='请求体不能为空')
        
        # 必填字段验证
        phone = data.get('phone', '').strip()
        if not phone:
            return api_response(code=400, message='手机号不能为空')
        
        # 验证手机号格式（简单验证）
        if not phone.isdigit() or len(phone) != 11:
            return api_response(code=400, message='手机号格式不正确')
        
        # 检查手机号是否已存在
        existing_lead = Lead.query.filter_by(phone=phone).first()
        if existing_lead:
            # 更新现有线索的跟进次数和最后跟进时间
            existing_lead.follow_count += 1
            existing_lead.last_follow_at = datetime.utcnow()
            
            # 如果提供了新的意向信息，更新备注
            if data.get('intention'):
                new_remark = f"[{datetime.now().strftime('%Y-%m-%d')}] 再次留资: {data.get('intention')}"
                existing_lead.remark = f"{existing_lead.remark or ''}\n{new_remark}".strip()
            
            db.session.commit()
            
            return api_response(
                code=200, 
                message='您已提交过信息，我们会尽快联系您',
                data=existing_lead.to_dict()
            )
        
        # 创建新线索
        lead = Lead(
            name=data.get('name', '').strip(),
            phone=phone,
            source=data.get('source', '网站留资'),
            source_id=data.get('source_id'),
            source_page=data.get('source_page'),
            intention=data.get('intention', '').strip(),
            budget=data.get('budget'),
            house_type=data.get('house_type'),
            area=data.get('area'),
            status=Lead.STATUS_NEW,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500],
            tenant_id=data.get('tenant_id', 'default')
        )
        
        db.session.add(lead)
        db.session.commit()
        
        return api_response(
            code=201, 
            message='提交成功，我们会尽快联系您',
            data=lead.to_dict()
        )
        
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'提交失败: {str(e)}')


@lead_bp.route('/leads', methods=['GET'])
def get_leads():
    """
    获取线索列表（管理端）
    
    查询参数:
    - status: 状态筛选 (新线索/已联系/已到店/已成交/无效)
    - assigned_to: 分配员工ID
    - source: 来源筛选
    - keyword: 关键词搜索（姓名/手机号）
    - start_date: 开始日期 (YYYY-MM-DD)
    - end_date: 结束日期 (YYYY-MM-DD)
    - page: 页码，默认1
    - page_size: 每页数量，默认10
    - sort_by: 排序字段
    - sort_order: 排序方向
    """
    try:
        # 获取查询参数
        status = request.args.get('status')
        assigned_to = request.args.get('assigned_to', type=int)
        source = request.args.get('source')
        keyword = request.args.get('keyword', '').strip()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 限制分页大小
        page_size = min(max(page_size, 1), 100)
        
        # 构建查询
        query = Lead.query
        
        # 状态筛选
        if status:
            query = query.filter(Lead.status == status)
        
        # 分配人筛选
        if assigned_to:
            query = query.filter(Lead.assigned_to == assigned_to)
        
        # 来源筛选
        if source:
            query = query.filter(Lead.source == source)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    Lead.name.contains(keyword),
                    Lead.phone.contains(keyword),
                    Lead.intention.contains(keyword)
                )
            )
        
        # 日期范围筛选
        if start_date:
            query = query.filter(Lead.created_at >= f"{start_date} 00:00:00")
        if end_date:
            query = query.filter(Lead.created_at <= f"{end_date} 23:59:59")
        
        # 排序
        sort_column = getattr(Lead, sort_by, Lead.created_at)
        if sort_order == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # 分页
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        # 构建响应
        data = {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'total_pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
        
        return api_response(data=data)
        
    except Exception as e:
        return api_response(code=500, message=f'获取线索列表失败: {str(e)}')


@lead_bp.route('/leads/<int:lead_id>', methods=['GET'])
def get_lead_detail(lead_id):
    """
    获取线索详情
    
    路径参数:
    - lead_id: 线索ID
    
    查询参数:
    - include_follows: 是否包含跟进记录 (默认true)
    """
    try:
        include_follows = request.args.get('include_follows', 'true').lower() == 'true'
        
        lead = Lead.query.get(lead_id)
        
        if not lead:
            return api_response(code=404, message='线索不存在')
        
        return api_response(data=lead.to_dict(include_follows=include_follows))
        
    except Exception as e:
        return api_response(code=500, message=f'获取线索详情失败: {str(e)}')


@lead_bp.route('/leads/<int:lead_id>/assign', methods=['PUT'])
def assign_lead(lead_id):
    """
    分配线索给员工
    
    路径参数:
    - lead_id: 线索ID
    
    请求体:
    {
        "assigned_to": 123
    }
    """
    try:
        lead = Lead.query.get(lead_id)
        
        if not lead:
            return api_response(code=404, message='线索不存在')
        
        data = request.get_json()
        assigned_to = data.get('assigned_to')
        
        if not assigned_to:
            return api_response(code=400, message='分配员工ID不能为空')
        
        lead.assign_to(assigned_to)
        
        return api_response(message='分配成功', data=lead.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'分配失败: {str(e)}')


@lead_bp.route('/leads/<int:lead_id>/status', methods=['PUT'])
def update_lead_status(lead_id):
    """
    更新线索状态
    
    路径参数:
    - lead_id: 线索ID
    
    请求体:
    {
        "status": "已联系"
    }
    """
    try:
        lead = Lead.query.get(lead_id)
        
        if not lead:
            return api_response(code=404, message='线索不存在')
        
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return api_response(code=400, message='状态不能为空')
        
        # 验证状态值
        valid_statuses = [Lead.STATUS_NEW, Lead.STATUS_CONTACTED, Lead.STATUS_VISITED, 
                         Lead.STATUS_DEAL, Lead.STATUS_INVALID]
        if status not in valid_statuses:
            return api_response(code=400, message=f'无效的状态值，可选: {valid_statuses}')
        
        lead.update_status(status)
        
        return api_response(message='状态更新成功', data=lead.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'更新状态失败: {str(e)}')


@lead_bp.route('/leads/<int:lead_id>/follow', methods=['POST'])
def add_lead_follow(lead_id):
    """
    添加跟进记录
    
    路径参数:
    - lead_id: 线索ID
    
    请求体:
    {
        "follow_type": "电话",
        "content": "客户意向强烈，约明天到店",
        "next_follow_at": "2026-04-26 10:00:00",
        "operator_id": 123
    }
    """
    try:
        lead = Lead.query.get(lead_id)
        
        if not lead:
            return api_response(code=404, message='线索不存在')
        
        data = request.get_json()
        
        if not data or not data.get('content'):
            return api_response(code=400, message='跟进内容不能为空')
        
        # 解析下次跟进时间
        next_follow_at = None
        if data.get('next_follow_at'):
            try:
                next_follow_at = datetime.strptime(data.get('next_follow_at'), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return api_response(code=400, message='下次跟进时间格式错误，应为: YYYY-MM-DD HH:MM:SS')
        
        # 添加跟进记录
        follow = lead.add_follow(
            follow_type=data.get('follow_type', '其他'),
            content=data.get('content'),
            next_follow_at=next_follow_at,
            operator_id=data.get('operator_id')
        )
        
        return api_response(
            code=201,
            message='跟进记录添加成功',
            data=follow.to_dict()
        )
        
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'添加跟进记录失败: {str(e)}')


@lead_bp.route('/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """
    更新线索信息
    
    路径参数:
    - lead_id: 线索ID
    """
    try:
        lead = Lead.query.get(lead_id)
        
        if not lead:
            return api_response(code=404, message='线索不存在')
        
        data = request.get_json()
        
        if not data:
            return api_response(code=400, message='请求体不能为空')
        
        # 可更新字段
        updatable_fields = [
            'name', 'intention', 'budget', 'house_type', 'area', 'remark'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(lead, field, data[field])
        
        db.session.commit()
        
        return api_response(message='线索更新成功', data=lead.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'更新线索失败: {str(e)}')


@lead_bp.route('/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """
    删除线索
    
    路径参数:
    - lead_id: 线索ID
    """
    try:
        lead = Lead.query.get(lead_id)
        
        if not lead:
            return api_response(code=404, message='线索不存在')
        
        db.session.delete(lead)
        db.session.commit()
        
        return api_response(message='线索删除成功')
        
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'删除线索失败: {str(e)}')


@lead_bp.route('/leads/stats', methods=['GET'])
def get_lead_stats():
    """
    获取线索统计
    
    返回各状态线索数量统计
    """
    try:
        from sqlalchemy import func
        
        # 按状态统计
        status_stats = db.session.query(
            Lead.status,
            func.count(Lead.id)
        ).group_by(Lead.status).all()
        
        # 今日新增
        today = datetime.now().strftime('%Y-%m-%d')
        today_count = Lead.query.filter(
            Lead.created_at >= f"{today} 00:00:00"
        ).count()
        
        # 本周新增
        from datetime import timedelta
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        week_count = Lead.query.filter(
            Lead.created_at >= f"{week_ago} 00:00:00"
        ).count()
        
        return api_response(data={
            'status_stats': {s: c for s, c in status_stats},
            'today_count': today_count,
            'week_count': week_count,
            'total_count': Lead.query.count()
        })
        
    except Exception as e:
        return api_response(code=500, message=f'获取统计失败: {str(e)}')


@lead_bp.route('/leads/sources', methods=['GET'])
def get_lead_sources():
    """
    获取线索来源列表
    
    返回所有不重复的线索来源
    """
    try:
        sources = db.session.query(Lead.source).distinct().all()
        return api_response(data=[s[0] for s in sources if s[0]])
    except Exception as e:
        return api_response(code=500, message=f'获取来源列表失败: {str(e)}')
