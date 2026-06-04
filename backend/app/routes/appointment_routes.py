"""
预约量尺模块路由
API端点: /api/v3/appointments
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, asc
from datetime import datetime, timedelta
from app import db
from app.models.appointment import Appointment
from app.models.lead_v2 import Lead


appointment_bp = Blueprint('appointment', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


@appointment_bp.route('/appointments', methods=['POST'])
def create_appointment():
    """
    提交预约（对外接口）
    
    请求体:
    {
        "customer_name": "张三",
        "phone": "13800138000",
        "house_address": "北京市朝阳区xxx",
        "house_type": "三室两厅",
        "area": "120",
        "budget": "30-50万",
        "appointment_date": "2025-04-30",
        "appointment_time": "14:00",
        "remark": "周末方便"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return api_response(code=400, message='请求体不能为空')
        
        # 必填字段验证
        customer_name = data.get('customer_name', '').strip()
        phone = data.get('phone', '').strip()
        
        if not customer_name:
            return api_response(code=400, message='客户姓名不能为空')
        if not phone:
            return api_response(code=400, message='手机号不能为空')
        
        # 手机号格式验证
        import re
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return api_response(code=400, message='手机号格式不正确')
        
        # 解析预约日期时间
        appointment_date = None
        appointment_time = None
        
        if data.get('appointment_date'):
            try:
                appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
            except ValueError:
                return api_response(code=400, message='预约日期格式错误')
        
        if data.get('appointment_time'):
            try:
                appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
            except ValueError:
                return api_response(code=400, message='预约时间格式错误')
        
        # 提取来源信息（Referer + UTM）
        referer = request.headers.get('Referer', '')
        utm_source = data.get('utm_source', '')
        utm_medium = data.get('utm_medium', '')
        utm_campaign = data.get('utm_campaign', '')
        landing_page = data.get('landing_page', referer)
        
        # 判断来源渠道
        if utm_source:
            source_channel = utm_source
        elif '/book' in referer or '/appointment' in referer:
            source_channel = '预约量尺页'
        elif '/selection-center' in referer:
            source_channel = '选品中心'
        elif '/products' in referer:
            source_channel = '产品中心'
        elif '/cases' in referer:
            source_channel = '案例列表'
        else:
            source_channel = '官网'
        
        # 创建预约
        appointment = Appointment(
            customer_name=customer_name,
            phone=phone,
            house_address=data.get('house_address', '').strip(),
            house_type=data.get('house_type'),
            area=data.get('area'),
            budget=data.get('budget'),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            remark=data.get('remark', '').strip(),
            ip_address=request.remote_addr,
            tenant_id='default'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # 自动创建线索（手机号唯一，查重）
        existing_lead = Lead.query.filter_by(phone=phone).first()
        if not existing_lead:
            lead = Lead(
                name=customer_name,
                phone=phone,
                wechat=data.get('wechat', '').strip() or None,
                source=source_channel,
                source_page=landing_page,
                source_detail=f"预约日期:{appointment_date} {appointment_time}" if appointment_date else '预约量尺',
                house_type=data.get('house_type'),
                area=float(data.get('area', 0)) if data.get('area') else None,
                budget=data.get('budget'),
                building_address=data.get('house_address', '').strip(),
                status='待分配',
                intention_level='高',
                conversion_level='线索',
                remark=f"预约量尺提交: {data.get('remark', '').strip()}".strip() or None,
                appointment_id=appointment.id,
                ip_address=request.remote_addr
            )
            db.session.add(lead)
            db.session.commit()
        else:
            # 已存在线索：追加来源记录 + 更新意向
            if existing_lead.remark:
                existing_lead.remark += f"\n[追加-{datetime.now().strftime('%Y-%m-%d')}] 预约量尺提交"
            else:
                existing_lead.remark = f"[追加-{datetime.now().strftime('%Y-%m-%d')}] 预约量尺提交"
            existing_lead.appointment_id = appointment.id
            if existing_lead.intention_level in [None, '', '低']:
                existing_lead.intention_level = '中'
            db.session.commit()
        
        return api_response(code=201, message='预约提交成功', data=appointment.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'提交预约失败: {str(e)}')


@appointment_bp.route('/appointments', methods=['GET'])
def get_appointments():
    """
    获取预约列表（管理端）
    
    查询参数:
    - status: 状态筛选
    - date_from: 开始日期
    - date_to: 结束日期
    - keyword: 关键词搜索
    - page: 页码
    - page_size: 每页数量
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        keyword = request.args.get('keyword', '').strip()
        
        # 构建查询
        query = Appointment.query
        
        if status:
            query = query.filter(Appointment.status == status)
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(Appointment.appointment_date >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(Appointment.appointment_date <= to_date)
            except ValueError:
                pass
        
        if keyword:
            query = query.filter(
                db.or_(
                    Appointment.customer_name.contains(keyword),
                    Appointment.phone.contains(keyword),
                    Appointment.house_address.contains(keyword)
                )
            )
        
        # 排序和分页
        query = query.order_by(desc(Appointment.created_at))
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return api_response(data={
            'items': [item.to_dict() for item in items],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
        
    except Exception as e:
        return api_response(code=500, message=f'获取预约列表失败: {str(e)}')


@appointment_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment_detail(appointment_id):
    """获取预约详情"""
    try:
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            return api_response(code=404, message='预约不存在')
        
        return api_response(data=appointment.to_dict())
        
    except Exception as e:
        return api_response(code=500, message=f'获取预约详情失败: {str(e)}')


@appointment_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    """
    更新预约
    
    可更新字段: status, assigned_to, remark, appointment_date, appointment_time
    """
    try:
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            return api_response(code=404, message='预约不存在')
        
        data = request.get_json()
        if not data:
            return api_response(code=400, message='请求体不能为空')
        
        # 更新状态
        if 'status' in data:
            new_status = data['status']
            if new_status == Appointment.STATUS_CONFIRMED:
                appointment.confirm()
            elif new_status == Appointment.STATUS_CANCELLED:
                appointment.cancel(data.get('cancel_reason'))
            elif new_status == Appointment.STATUS_COMPLETED:
                appointment.complete()
            else:
                appointment.status = new_status
        
        # 更新其他字段
        if 'assigned_to' in data:
            appointment.assigned_to = data['assigned_to']
        
        if 'remark' in data:
            appointment.remark = data['remark']
        
        if 'appointment_date' in data and data['appointment_date']:
            try:
                appointment.appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
            except ValueError:
                return api_response(code=400, message='预约日期格式错误')
        
        if 'appointment_time' in data and data['appointment_time']:
            try:
                appointment.appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
            except ValueError:
                return api_response(code=400, message='预约时间格式错误')
        
        db.session.commit()
        
        return api_response(message='预约更新成功', data=appointment.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'更新预约失败: {str(e)}')


@appointment_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    """删除预约"""
    try:
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            return api_response(code=404, message='预约不存在')
        
        db.session.delete(appointment)
        db.session.commit()
        
        return api_response(message='预约删除成功')
        
    except Exception as e:
        db.session.rollback()
        return api_response(code=500, message=f'删除预约失败: {str(e)}')


@appointment_bp.route('/appointments/stats', methods=['GET'])
def get_appointment_stats():
    """获取预约统计"""
    try:
        # 总预约数
        total = Appointment.query.count()
        
        # 各状态统计
        status_stats = db.session.query(
            Appointment.status,
            db.func.count(Appointment.id)
        ).group_by(Appointment.status).all()
        
        # 今日预约
        today = datetime.now().date()
        today_count = Appointment.query.filter(
            db.func.date(Appointment.appointment_date) == today
        ).count()
        
        # 本周预约
        week_start = today - timedelta(days=today.weekday())
        week_count = Appointment.query.filter(
            Appointment.appointment_date >= week_start
        ).count()
        
        return api_response(data={
            'total_count': total,
            'today_count': today_count,
            'week_count': week_count,
            'status_stats': {status: count for status, count in status_stats}
        })
        
    except Exception as e:
        return api_response(code=500, message=f'获取统计失败: {str(e)}')


@appointment_bp.route('/appointments/calendar', methods=['GET'])
def get_appointment_calendar():
    """
    获取预约日历数据
    
    查询参数:
    - year: 年份
    - month: 月份
    """
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # 计算月份起止日期
        from datetime import date
        import calendar
        
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        # 查询该月所有预约
        appointments = Appointment.query.filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date,
            Appointment.status != Appointment.STATUS_CANCELLED
        ).order_by(Appointment.appointment_time).all()
        
        # 按日期分组
        calendar_data = {}
        for apt in appointments:
            date_str = apt.appointment_date.isoformat()
            if date_str not in calendar_data:
                calendar_data[date_str] = []
            calendar_data[date_str].append({
                'id': apt.id,
                'customer_name': apt.customer_name,
                'time': apt.appointment_time.isoformat() if apt.appointment_time else None,
                'status': apt.status
            })
        
        return api_response(data=calendar_data)
        
    except Exception as e:
        return api_response(code=500, message=f'获取日历数据失败: {str(e)}')
