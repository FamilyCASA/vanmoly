"""
数据看板模块路由
API端点: /api/v3/dashboard
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func

from app import db
from app.models.customer import Customer
from app.models.contract import Contract
from app.models.material_sku import MaterialSKU
from app.models.building import Building
from app.models import Employee  # 从 hr_v2 导入
from app.models.lead_v2 import Lead
from app.models.quote import Quote
from app.models.appointment import Appointment
from app.models.case import CaseStudy

dashboard_bp = Blueprint('dashboard', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


@dashboard_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """获取看板核心统计数据"""
    try:
        # 客户总数
        customer_count = Customer.query.count()
        
        # 合同统计
        contract_count = Contract.query.count()
        contract_amount = db.session.query(func.sum(Contract.total_amount)).scalar() or 0
        
        # 物料总数
        material_count = MaterialSKU.query.count()
        
        # 楼盘总数
        building_count = Building.query.count()
        
        # 员工总数
        employee_count = Employee.query.count()
        
        # 今日新增
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_customers = Customer.query.filter(
            Customer.created_at >= today_start,
            Customer.created_at <= today_end
        ).count()
        
        today_leads = Lead.query.filter(
            Lead.created_at >= today_start,
            Lead.created_at <= today_end
        ).count()
        
        # 本周数据
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_customers = Customer.query.filter(Customer.created_at >= week_start_dt).count()
        week_contracts = Contract.query.filter(Contract.created_at >= week_start_dt).count()
        
        # 本月数据
        month_start = today.replace(day=1)
        month_start_dt = datetime.combine(month_start, datetime.min.time())
        month_amount = db.session.query(func.sum(Contract.total_amount)).filter(
            Contract.created_at >= month_start_dt
        ).scalar() or 0
        
        # 待办事项统计
        pending_quotes = Quote.query.filter(Quote.status == 'draft').count()
        low_stock_materials = MaterialSKU.query.filter(MaterialSKU.stock_quantity <= 10).count()
        pending_appointments = Appointment.query.filter(
            Appointment.status == 'pending'
        ).count()
        
        return api_response(data={
            'overview': {
                'customers': customer_count,
                'contracts': contract_count,
                'contractAmount': float(contract_amount),
                'materials': material_count,
                'buildings': building_count,
                'employees': employee_count
            },
            'today': {
                'newCustomers': today_customers,
                'newLeads': today_leads
            },
            'week': {
                'newCustomers': week_customers,
                'newContracts': week_contracts
            },
            'month': {
                'contractAmount': float(month_amount)
            },
            'todo': {
                'pendingQuotes': pending_quotes,
                'lowStockMaterials': low_stock_materials,
                'pendingAppointments': pending_appointments
            }
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@dashboard_bp.route('/dashboard/trends', methods=['GET'])
def get_trends():
    """获取业务趋势数据"""
    try:
        period = request.args.get('period', 'week')
        
        if period == 'week':
            # 最近7天数据
            days = 7
            date_format = '%m-%d'
        elif period == 'month':
            days = 30
            date_format = '%m-%d'
        else:  # year
            days = 365
            date_format = '%Y-%m'
        
        dates = []
        new_customers = []
        new_contracts = []
        new_quotes = []
        
        for i in range(days - 1, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            date_start = datetime.combine(date, datetime.min.time())
            date_end = datetime.combine(date, datetime.max.time())
            
            dates.append(date.strftime(date_format))
            
            # 每日新增客户
            customer_count = Customer.query.filter(
                Customer.created_at >= date_start,
                Customer.created_at <= date_end
            ).count()
            new_customers.append(customer_count)
            
            # 每日新增合同金额
            contract_amount = db.session.query(func.sum(Contract.total_amount)).filter(
                Contract.created_at >= date_start,
                Contract.created_at <= date_end
            ).scalar() or 0
            new_contracts.append(float(contract_amount))
            
            # 每日新增报价
            quote_count = Quote.query.filter(
                Quote.created_at >= date_start,
                Quote.created_at <= date_end
            ).count()
            new_quotes.append(quote_count)
        
        return api_response(data={
            'dates': dates,
            'newCustomers': new_customers,
            'contractAmount': new_contracts,
            'newQuotes': new_quotes
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@dashboard_bp.route('/dashboard/contract-distribution', methods=['GET'])
def get_contract_distribution():
    """获取合同金额分布"""
    try:
        # 按金额区间统计
        ranges = [
            {'name': '10万以下', 'min': 0, 'max': 100000},
            {'name': '10-20万', 'min': 100000, 'max': 200000},
            {'name': '20-30万', 'min': 200000, 'max': 300000},
            {'name': '30-50万', 'min': 300000, 'max': 500000},
            {'name': '50万以上', 'min': 500000, 'max': float('inf')}
        ]
        
        distribution = []
        for r in ranges:
            count = Contract.query.filter(
                Contract.total_amount >= r['min'],
                Contract.total_amount < r['max'] if r['max'] != float('inf') else Contract.total_amount >= r['min']
            ).count()
            amount = db.session.query(func.sum(Contract.total_amount)).filter(
                Contract.total_amount >= r['min'],
                Contract.total_amount < r['max'] if r['max'] != float('inf') else Contract.total_amount >= r['min']
            ).scalar() or 0
            
            distribution.append({
                'name': r['name'],
                'count': count,
                'amount': float(amount)
            })
        
        return api_response(data=distribution)
    except Exception as e:
        return api_response(code=500, message=str(e))


@dashboard_bp.route('/dashboard/recent-activities', methods=['GET'])
def get_recent_activities():
    """获取最近动态"""
    try:
        limit = request.args.get('limit', 10, type=int)
        activities = []
        
        # 最近客户
        recent_customers = Customer.query.order_by(Customer.created_at.desc()).limit(5).all()
        for c in recent_customers:
            activities.append({
                'type': 'primary',
                'content': f'新客户 {c.name} 录入系统',
                'time': c.created_at.strftime('%Y-%m-%d %H:%M'),
                'timestamp': c.created_at
            })
        
        # 最近合同
        recent_contracts = Contract.query.order_by(Contract.created_at.desc()).limit(5).all()
        for ct in recent_contracts:
            activities.append({
                'type': 'success',
                'content': f'合同 {ct.contract_no} 已签约，金额 ¥{float(ct.total_amount):,.0f}',
                'time': ct.created_at.strftime('%Y-%m-%d %H:%M'),
                'timestamp': ct.created_at
            })
        
        # 最近报价
        recent_quotes = Quote.query.order_by(Quote.created_at.desc()).limit(5).all()
        for q in recent_quotes:
            activities.append({
                'type': 'info',
                'content': f'报价单 {q.quote_no} 已创建',
                'time': q.created_at.strftime('%Y-%m-%d %H:%M'),
                'timestamp': q.created_at
            })
        
        # 按时间排序
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        activities = activities[:limit]
        
        # 移除 timestamp 字段
        for a in activities:
            del a['timestamp']
        
        return api_response(data=activities)
    except Exception as e:
        return api_response(code=500, message=str(e))


@dashboard_bp.route('/dashboard/funnel', methods=['GET'])
def get_funnel():
    """获取获客漏斗数据"""
    try:
        # 线索总数
        total_leads = Lead.query.count()
        
        # 已联系
        contacted = Lead.query.filter(Lead.status.in_(['contacted', 'visited', 'converted'])).count()
        
        # 已到访
        visited = Lead.query.filter(Lead.status.in_(['visited', 'converted'])).count()
        
        # 已成交（转为客户的线索）
        deals = Lead.query.filter(Lead.status == 'converted').count()
        
        # 转化率
        conversion_rate = round(deals / total_leads * 100, 1) if total_leads > 0 else 0
        
        return api_response(data={
            'new_leads': total_leads,
            'contacted': contacted,
            'visited': visited,
            'deals': deals,
            'conversion_rate': conversion_rate
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@dashboard_bp.route('/dashboard/case-stats', methods=['GET'])
def get_case_stats():
    """获取案例统计数据"""
    try:
        total_cases = CaseStudy.query.count()
        
        # 总浏览量
        total_views = db.session.query(func.sum(CaseStudy.view_count)).scalar() or 0
        
        # 总点赞数
        total_likes = db.session.query(func.sum(CaseStudy.like_count)).scalar() or 0
        
        return api_response(data={
            'total_cases': total_cases,
            'total_views': int(total_views),
            'total_likes': int(total_likes),
            'lead_conversion': 0  # 待实现
        })
    except Exception as e:
        return api_response(code=500, message=str(e))


@dashboard_bp.route('/dashboard/lead-stats', methods=['GET'])
def get_lead_stats():
    """获取获客数据"""
    try:
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        week_start = today - timedelta(days=today.weekday())
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        
        month_start = today.replace(day=1)
        month_start_dt = datetime.combine(month_start, datetime.min.time())
        
        today_leads = Lead.query.filter(Lead.created_at >= today_start).count()
        week_leads = Lead.query.filter(Lead.created_at >= week_start_dt).count()
        month_leads = Lead.query.filter(Lead.created_at >= month_start_dt).count()
        
        return api_response(data={
            'today_leads': today_leads,
            'week_leads': week_leads,
            'month_leads': month_leads
        })
    except Exception as e:
        return api_response(code=500, message=str(e))
