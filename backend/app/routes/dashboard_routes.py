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
            # 安全处理 created_at（可能是字符串或 datetime）
            created_at_str = c.created_at
            if hasattr(c.created_at, 'strftime'):
                created_at_str = c.created_at.strftime('%Y-%m-%d %H:%M')
            activities.append({
                'type': 'primary',
                'content': f'新客户 {c.name} 录入系统',
                'time': created_at_str,
                'timestamp': c.created_at
            })
        
        # 最近合同
        recent_contracts = Contract.query.order_by(Contract.created_at.desc()).limit(5).all()
        for ct in recent_contracts:
            # 安全处理 created_at
            created_at_str = ct.created_at
            if hasattr(ct.created_at, 'strftime'):
                created_at_str = ct.created_at.strftime('%Y-%m-%d %H:%M')
            activities.append({
                'type': 'success',
                'content': f'合同 {ct.contract_no} 已签约，金额 ¥{float(ct.total_amount):,.0f}',
                'time': created_at_str,
                'timestamp': ct.created_at
            })
        
        # 最近报价
        recent_quotes = Quote.query.order_by(Quote.created_at.desc()).limit(5).all()
        for q in recent_quotes:
            # 安全处理 created_at
            created_at_str = q.created_at
            if hasattr(q.created_at, 'strftime'):
                created_at_str = q.created_at.strftime('%Y-%m-%d %H:%M')
            activities.append({
                'type': 'info',
                'content': f'报价单 {q.quote_no} 已创建',
                'time': created_at_str,
                'timestamp': q.created_at
            })
        
        # 按时间排序（统一为字符串处理）
        def _sort_key(a):
            v = a['timestamp']
            if v is None:
                return '0000-00-00'
            if hasattr(v, 'strftime'):
                return v.strftime('%Y-%m-%d %H:%M:%S')
            return str(v)
        activities.sort(key=_sort_key, reverse=True)
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


@dashboard_bp.route('/dashboard/overview', methods=['GET'])
def get_overview():
    """综合数据概览 - 数据驾驶舱核心接口"""
    try:
        from app.models.finance import FinanceTransaction, FinanceReimbursement, FinanceReceivable, FinancePayable
        
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        month_start = today.replace(day=1)
        month_start_dt = datetime.combine(month_start, datetime.min.time())
        
        # ===== 核心指标 =====
        total_customers = Customer.query.filter_by(is_deleted=False).count()
        total_leads = Lead.query.count()
        total_quotes = Quote.query.count()
        total_contracts = Contract.query.count()
        total_buildings = Building.query.count()
        total_employees = Employee.query.count()
        
        # 今日新增
        today_new_customers = Customer.query.filter(
            Customer.is_deleted == False,
            Customer.created_at >= today_start
        ).count()
        today_new_leads = Lead.query.filter(Lead.created_at >= today_start).count()
        today_new_quotes = Quote.query.filter(Quote.created_at >= today_start).count()
        
        # 本月新增
        month_new_customers = Customer.query.filter(
            Customer.is_deleted == False,
            Customer.created_at >= month_start_dt
        ).count()
        month_new_leads = Lead.query.filter(Lead.created_at >= month_start_dt).count()
        month_new_contracts = Contract.query.filter(Contract.created_at >= month_start_dt).count()
        
        # ===== 财务指标 =====
        total_income = db.session.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.trans_type == 'income',
            FinanceTransaction.status == 'approved'
        ).scalar() or 0
        
        total_expense = db.session.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.trans_type == 'expense',
            FinanceTransaction.status == 'approved'
        ).scalar() or 0
        
        month_income = db.session.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.trans_type == 'income',
            FinanceTransaction.status == 'approved',
            FinanceTransaction.trans_date >= month_start
        ).scalar() or 0
        
        month_expense = db.session.query(func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.trans_type == 'expense',
            FinanceTransaction.status == 'approved',
            FinanceTransaction.trans_date >= month_start
        ).scalar() or 0
        
        # 应收应付
        pending_receivable = db.session.query(func.sum(FinanceReceivable.amount)).filter(
            FinanceReceivable.status == 'pending'
        ).scalar() or 0
        pending_payable = db.session.query(func.sum(FinancePayable.amount)).filter(
            FinancePayable.status == 'pending'
        ).scalar() or 0
        
        # 报销统计
        pending_reimbursements = FinanceReimbursement.query.filter(
            FinanceReimbursement.status.in_(['submitted', 'pending'])
        ).count()
        
        # ===== 报价/合同金额 =====
        total_quote_amount = db.session.query(func.sum(Quote.total_amount)).scalar() or 0
        total_contract_amount = db.session.query(func.sum(Contract.total_amount)).scalar() or 0
        
        # 报价状态分布
        quote_status_dist = db.session.query(
            Quote.status, func.count(Quote.id)
        ).group_by(Quote.status).all()
        
        # 客户状态分布
        customer_status_dist = db.session.query(
            Customer.status, func.count(Customer.id)
        ).filter(Customer.is_deleted == False).group_by(Customer.status).all()
        
        # 客户来源分布
        customer_source_dist = db.session.query(
            Customer.source, func.count(Customer.id)
        ).filter(Customer.is_deleted == False, Customer.source != None).group_by(Customer.source).all()
        
        # ===== 待办事项 =====
        pending_quotes = Quote.query.filter(Quote.status == 'draft').count()
        pending_appointments = Appointment.query.filter(Appointment.status == 'pending').count()
        follow_up_customers = Customer.query.filter(
            Customer.is_deleted == False,
            Customer.status.in_(['待跟进', '跟进中'])
        ).count()
        
        # ===== 月度收支趋势（最近6个月）=====
        monthly_trend = []
        for i in range(5, -1, -1):
            m = today.month - i
            y = today.year
            if m <= 0:
                m += 12
                y -= 1
            m_start_date = datetime(y, m, 1).date()
            if m == 12:
                m_end_date = datetime(y + 1, 1, 1).date() - timedelta(days=1)
            else:
                m_end_date = datetime(y, m + 1, 1).date() - timedelta(days=1)
            if i == 0:
                m_end_date = today
            
            m_income = db.session.query(func.sum(FinanceTransaction.amount)).filter(
                FinanceTransaction.trans_type == 'income',
                FinanceTransaction.status == 'approved',
                FinanceTransaction.trans_date >= m_start_date,
                FinanceTransaction.trans_date <= m_end_date
            ).scalar() or 0
            
            m_expense = db.session.query(func.sum(FinanceTransaction.amount)).filter(
                FinanceTransaction.trans_type == 'expense',
                FinanceTransaction.status == 'approved',
                FinanceTransaction.trans_date >= m_start_date,
                FinanceTransaction.trans_date <= m_end_date
            ).scalar() or 0
            
            monthly_trend.append({
                'month': f'{y}-{m:02d}',
                'income': float(m_income),
                'expense': float(m_expense)
            })
        
        return api_response(data={
            # 核心指标
            'core': {
                'total_customers': total_customers,
                'total_leads': total_leads,
                'total_quotes': total_quotes,
                'total_contracts': total_contracts,
                'total_buildings': total_buildings,
                'total_employees': total_employees,
            },
            'today': {
                'new_customers': today_new_customers,
                'new_leads': today_new_leads,
                'new_quotes': today_new_quotes,
            },
            'month': {
                'new_customers': month_new_customers,
                'new_leads': month_new_leads,
                'new_contracts': month_new_contracts,
            },
            # 财务
            'finance': {
                'total_income': float(total_income),
                'total_expense': float(total_expense),
                'total_profit': float(total_income) - float(total_expense),
                'month_income': float(month_income),
                'month_expense': float(month_expense),
                'month_profit': float(month_income) - float(month_expense),
                'pending_receivable': float(pending_receivable),
                'pending_payable': float(pending_payable),
                'pending_reimbursements': pending_reimbursements,
                'total_quote_amount': float(total_quote_amount),
                'total_contract_amount': float(total_contract_amount),
            },
            # 分布数据
            'distributions': {
                'quote_status': {s: c for s, c in quote_status_dist},
                'customer_status': {s: c for s, c in customer_status_dist},
                'customer_source': {s: c for s, c in customer_source_dist},
            },
            # 待办
            'todos': {
                'pending_quotes': pending_quotes,
                'pending_appointments': pending_appointments,
                'follow_up_customers': follow_up_customers,
                'pending_reimbursements': pending_reimbursements,
            },
            # 趋势
            'monthly_trend': monthly_trend,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return api_response(code=500, message=str(e))
