# -*- coding: utf-8 -*-
"""
财务管理模块路由 - V3.0

包含：
- 组织架构与权限管理
- 删除申请管理
- 流水管理
- 报销管理
- 投资管理
- 操作日志
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from decimal import Decimal
import json
import os
import stat
import hashlib

from app import db
from app.models.finance import (
    FinanceRole, FinanceMember, FinanceApprovalFlow, FinanceDeleteRequest,
    FinanceTransaction, FinanceCategory, FinanceReimbursement,
    FinanceShareholder, FinanceCharter, FinanceAuditLog,
    FinanceReceivable, FinancePayable, FinancePaymentPlan,
    FinanceDepartment, FinancePosition
)

finance_bp = Blueprint('finance', __name__, url_prefix='/api/v3/finance')



# ============================================================
# 辅助函数
# ============================================================

def get_current_user():
    """获取当前用户信息"""
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get('user_id'), identity.get('tenant_id', 'default')
    return int(identity), 'default'


def log_action(operator_id, action, target_type, target_id, detail_before=None, detail_after=None):
    """记录操作日志"""
    log = FinanceAuditLog(
        tenant_id='default',
        operator_id=operator_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail_before=json.dumps(detail_before) if detail_before else None,
        detail_after=json.dumps(detail_after) if detail_after else None,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')
    )
    db.session.add(log)
    db.session.commit()


def check_permission(user_id, permission):
    """检查用户是否有指定权限"""
    member = FinanceMember.query.filter_by(employee_id=user_id, is_active=True).first()
    if not member:
        return False
    
    role = member.role
    if not role:
        return False
    
    permissions = json.loads(role.permissions) if role.permissions else []
    return permission in permissions


def can_delete_directly(user_id):
    """检查用户是否可以直接删除"""
    member = FinanceMember.query.filter_by(employee_id=user_id, is_active=True).first()
    if not member:
        return False
    
    role = member.role
    if not role:
        return False
    
    return role.can_delete


def is_delete_unlocked(user_id):
    """检查用户的删除权限是否已解锁"""
    member = FinanceMember.query.filter_by(employee_id=user_id, is_active=True).first()
    if not member:
        return False
    
    if member.delete_unlock_until and member.delete_unlock_until > datetime.utcnow():
        return True
    
    return False


def generate_trans_no(trans_type):
    """生成流水编号"""
    prefix = 'FL' if trans_type == 'expense' else 'SR'
    today = datetime.now().strftime('%Y%m%d')
    
    # 查询今天的最大序号
    last_trans = FinanceTransaction.query.filter(
        FinanceTransaction.trans_no.like(f'{prefix}{today}%')
    ).order_by(FinanceTransaction.id.desc()).first()
    
    if last_trans:
        last_seq = int(last_trans.trans_no[-3:])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    
    return f'{prefix}{today}{new_seq:03d}'


def generate_reimb_no():
    """生成报销编号"""
    prefix = 'BX'
    today = datetime.now().strftime('%Y%m%d')
    
    last_reimb = FinanceReimbursement.query.filter(
        FinanceReimbursement.reimb_no.like(f'{prefix}{today}%')
    ).order_by(FinanceReimbursement.id.desc()).first()
    
    if last_reimb:
        last_seq = int(last_reimb.reimb_no[-3:])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    
    return f'{prefix}{today}{new_seq:03d}'


# ============================================================
# 组织架构与权限管理
# ============================================================

@finance_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """获取财务角色列表"""
    try:
        roles = FinanceRole.query.filter_by(is_system=True).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [role.to_dict() for role in roles]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/members', methods=['GET'])
@jwt_required()
def get_members():
    """获取财务团队成员列表"""
    try:
        members = FinanceMember.query.filter_by(is_active=True).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [member.to_dict() for member in members]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/members', methods=['POST'])
@jwt_required()
def add_member():
    """添加财务团队成员"""
    try:
        user_id, tenant_id = get_current_user()
        
        # 检查权限
        if not check_permission(user_id, 'settings'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        data = request.get_json()
        
        # 检查员工是否已存在
        existing = FinanceMember.query.filter_by(employee_id=data['employee_id']).first()
        if existing:
            return jsonify({'code': 400, 'message': '该员工已是财务团队成员', 'data': None}), 400
        
        member = FinanceMember(
            tenant_id=tenant_id,
            employee_id=data['employee_id'],
            role_id=data['role_id'],
            assigned_by=user_id,
            is_active=True
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '添加成功',
            'data': member.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/members/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_member(member_id):
    """修改成员角色"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'settings'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        member = FinanceMember.query.get_or_404(member_id)
        data = request.get_json()
        
        member.role_id = data.get('role_id', member.role_id)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '修改成功',
            'data': member.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_member(member_id):
    """移除财务团队成员"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'settings'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        member = FinanceMember.query.get_or_404(member_id)
        member.is_active = False
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '移除成功',
            'data': None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/my-permissions', methods=['GET'])
@jwt_required()
def get_my_permissions():
    """获取当前用户的财务权限"""
    try:
        user_id, tenant_id = get_current_user()
        
        member = FinanceMember.query.filter_by(employee_id=user_id, is_active=True).first()
        
        if not member:
            return jsonify({
                'code': 200,
                'message': '该用户不是财务团队成员',
                'data': {
                    'is_member': False,
                    'permissions': []
                }
            })
        
        role = member.role
        permissions = json.loads(role.permissions) if role.permissions else []
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'is_member': True,
                'role_name': role.role_name if role else None,
                'permissions': permissions,
                'can_delete': can_delete_directly(user_id)
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/financial-staff', methods=['GET'])
@jwt_required()
def get_financial_staff():
    """获取所有财务人员（用于通知）"""
    try:
        members = FinanceMember.query.filter_by(is_active=True).all()
        
        # 获取员工详情（从 Employee 表）
        result = []
        for member in members:
            result.append({
                'member_id': member.id,
                'employee_id': member.employee_id,
                'role_name': member.role.role_name if member.role else None,
                'role_code': member.role.role_code if member.role else None
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


# ============================================================
# 删除申请管理
# ============================================================

@finance_bp.route('/delete-requests', methods=['POST'])
@jwt_required()
def create_delete_request():
    """提交删除申请"""
    try:
        user_id, tenant_id = get_current_user()
        data = request.get_json()
        
        # 检查流水是否存在
        transaction = FinanceTransaction.query.get(data['transaction_id'])
        if not transaction:
            return jsonify({'code': 404, 'message': '流水不存在', 'data': None}), 404
        
        # 检查是否已有待审批的删除申请
        existing = FinanceDeleteRequest.query.filter_by(
            transaction_id=data['transaction_id'],
            status='pending'
        ).first()
        
        if existing:
            return jsonify({'code': 400, 'message': '该流水已有待审批的删除申请', 'data': None}), 400
        
        delete_request = FinanceDeleteRequest(
            tenant_id=tenant_id,
            transaction_id=data['transaction_id'],
            applicant_id=user_id,
            reason=data['reason'],
            status='pending'
        )
        
        db.session.add(delete_request)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除申请已提交，请等待超级管理员审批',
            'data': delete_request.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/delete-requests', methods=['GET'])
@jwt_required()
def get_delete_requests():
    """获取删除申请列表"""
    try:
        user_id, tenant_id = get_current_user()
        
        status = request.args.get('status', 'all')
        
        query = FinanceDeleteRequest.query
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        delete_requests = query.order_by(FinanceDeleteRequest.created_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [dr.to_dict() for dr in delete_requests]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/my-delete-requests', methods=['GET'])
@jwt_required()
def get_my_delete_requests():
    """获取我的删除申请"""
    try:
        user_id, tenant_id = get_current_user()
        
        delete_requests = FinanceDeleteRequest.query.filter_by(
            applicant_id=user_id
        ).order_by(FinanceDeleteRequest.created_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [dr.to_dict() for dr in delete_requests]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/pending-delete-requests', methods=['GET'])
@jwt_required()
def get_pending_delete_requests():
    """获取待审批的删除申请（超级管理员）"""
    try:
        user_id, tenant_id = get_current_user()
        
        # 检查是否是超级管理员
        if not can_delete_directly(user_id):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        delete_requests = FinanceDeleteRequest.query.filter_by(
            status='pending'
        ).order_by(FinanceDeleteRequest.created_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [dr.to_dict() for dr in delete_requests]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/delete-requests/<int:request_id>/approve', methods=['PUT'])
@jwt_required()
def approve_delete_request(request_id):
    """审批通过删除申请"""
    try:
        user_id, tenant_id = get_current_user()
        
        # 检查是否是超级管理员
        if not can_delete_directly(user_id):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        delete_request = FinanceDeleteRequest.query.get_or_404(request_id)
        
        if delete_request.status != 'pending':
            return jsonify({'code': 400, 'message': '该申请已处理', 'data': None}), 400
        
        data = request.get_json()
        
        delete_request.status = 'approved'
        delete_request.reviewed_by = user_id
        delete_request.reviewed_at = datetime.utcnow()
        delete_request.review_note = data.get('note', '')
        delete_request.unlock_until = datetime.utcnow() + timedelta(hours=24)
        
        # 解锁申请人的删除权限（24小时）
        member = FinanceMember.query.filter_by(
            employee_id=delete_request.applicant_id
        ).first()
        if member:
            member.delete_unlock_until = datetime.utcnow() + timedelta(hours=24)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '审批通过，申请人删除权限已解锁24小时',
            'data': delete_request.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/delete-requests/<int:request_id>/reject', methods=['PUT'])
@jwt_required()
def reject_delete_request(request_id):
    """审批驳回删除申请"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not can_delete_directly(user_id):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        delete_request = FinanceDeleteRequest.query.get_or_404(request_id)
        
        if delete_request.status != 'pending':
            return jsonify({'code': 400, 'message': '该申请已处理', 'data': None}), 400
        
        data = request.get_json()
        
        delete_request.status = 'rejected'
        delete_request.reviewed_by = user_id
        delete_request.reviewed_at = datetime.utcnow()
        delete_request.review_note = data.get('note', '')
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '审批已驳回',
            'data': delete_request.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


# ============================================================
# 流水管理
# ============================================================

@finance_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    """获取财务总览数据（增强版：含年度统计、月度趋势、分类占比、最近流水）"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'view'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        from datetime import datetime, timedelta
        import calendar
        today = datetime.now()
        month_start = datetime(today.year, today.month, 1)
        year_start = datetime(today.year, 1, 1)
        
        # === 基础查询条件 ===
        base_filter = FinanceTransaction.deleted_at.is_(None)
        
        # === 今日统计 ===
        today_income = db.session.query(db.func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.trans_type == 'income',
            FinanceTransaction.trans_date == today.date(),
            base_filter
        ).scalar() or 0
        today_expense = db.session.query(db.func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.trans_type == 'expense',
            FinanceTransaction.trans_date == today.date(),
            base_filter
        ).scalar() or 0
        
        # === 本月统计 ===
        month_income = db.session.query(db.func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.trans_type == 'income',
            FinanceTransaction.trans_date >= month_start.date(),
            base_filter
        ).scalar() or 0
        month_expense = db.session.query(db.func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.trans_type == 'expense',
            FinanceTransaction.trans_date >= month_start.date(),
            base_filter
        ).scalar() or 0
        
        # === 本年统计 ===
        year_income = db.session.query(db.func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.trans_type == 'income',
            FinanceTransaction.trans_date >= year_start.date(),
            base_filter
        ).scalar() or 0
        year_expense = db.session.query(db.func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.trans_type == 'expense',
            FinanceTransaction.trans_date >= year_start.date(),
            base_filter
        ).scalar() or 0
        
        # === 月度趋势（近12个月） ===
        monthly_trend = []
        for i in range(11, -1, -1):
            m = today.month - i
            y = today.year
            while m < 1:
                m += 12
                y -= 1
            while m > 12:
                m -= 12
                y += 1
            m_start = datetime(y, m, 1).date()
            _, last_day = calendar.monthrange(y, m)
            m_end = datetime(y, m, last_day).date()
            
            inc = db.session.query(db.func.sum(FinanceTransaction.amount)).filter(
                FinanceTransaction.trans_type == 'income',
                FinanceTransaction.trans_date >= m_start,
                FinanceTransaction.trans_date <= m_end,
                base_filter
            ).scalar() or 0
            exp_ = db.session.query(db.func.sum(FinanceTransaction.amount)).filter(
                FinanceTransaction.trans_type == 'expense',
                FinanceTransaction.trans_date >= m_start,
                FinanceTransaction.trans_date <= m_end,
                base_filter
            ).scalar() or 0
            
            monthly_trend.append({
                'month': f'{y}-{m:02d}',
                'income': float(inc),
                'expense': float(exp_),
                'balance': float(inc - exp_)
            })
        
        # === 本月分类占比 ===
        categories = db.session.query(
            FinanceTransaction.category_id,
            FinanceTransaction.trans_type,
            db.func.sum(FinanceTransaction.amount).label('total')
        ).filter(
            FinanceTransaction.trans_date >= month_start.date(),
            FinanceTransaction.trans_date <= today.date(),
            base_filter,
            FinanceTransaction.category_id.isnot(None)
        ).group_by(
            FinanceTransaction.category_id,
            FinanceTransaction.trans_type
        ).all()
        
        category_breakdown = []
        for cat_id, ctype, total in categories:
            cat = FinanceCategory.query.get(cat_id)
            cat_name = cat.name if cat else f'分类{cat_id}'
            category_breakdown.append({
                'category_id': cat_id,
                'category_name': cat_name,
                'type': ctype,
                'total': float(total) if total else 0
            })
        category_breakdown.sort(key=lambda x: x['total'], reverse=True)
        
        # === 最近流水 ===
        recent = FinanceTransaction.query.filter(base_filter).order_by(
            FinanceTransaction.trans_date.desc(),
            FinanceTransaction.id.desc()
        ).limit(5).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'today_income': float(today_income),
                'today_expense': float(today_expense),
                'today_balance': float(today_income - today_expense),
                'month_income': float(month_income),
                'month_expense': float(month_expense),
                'month_balance': float(month_income - month_expense),
                'year_income': float(year_income),
                'year_expense': float(year_expense),
                'year_balance': float(year_income - year_expense),
                'monthly_trend': monthly_trend,
                'category_breakdown': category_breakdown,
                'recent_transactions': [t.to_dict() for t in recent]
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """获取流水列表"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'view'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        # 筛选条件
        trans_type = request.args.get('type', 'all')
        category_id = request.args.get('category_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status', 'all')
        
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        query = FinanceTransaction.query.filter(FinanceTransaction.deleted_at.is_(None))
        
        if trans_type != 'all':
            query = query.filter_by(trans_type=trans_type)
        
        if category_id:
            query = query.filter_by(category_id=int(category_id))
        
        if start_date:
            query = query.filter(FinanceTransaction.trans_date >= start_date)
        
        if end_date:
            query = query.filter(FinanceTransaction.trans_date <= end_date)
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        total = query.count()
        
        # 汇总统计（基于当前筛选条件）
        filtered_ids = query.with_entities(FinanceTransaction.id).subquery()
        summary_income = db.session.query(db.func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.id.in_(filtered_ids),
            FinanceTransaction.trans_type == 'income'
        ).scalar() or 0
        summary_expense = db.session.query(db.func.sum(FinanceTransaction.amount)).filter(
            FinanceTransaction.id.in_(filtered_ids),
            FinanceTransaction.trans_type == 'expense'
        ).scalar() or 0
        
        transactions = query.order_by(FinanceTransaction.trans_date.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'summary_income': float(summary_income),
                'summary_expense': float(summary_expense),
                'items': [t.to_dict() for t in transactions]
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    """新增流水"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'input'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        data = request.get_json()
        
        # 验证凭证是否上传
        voucher_files = data.get('voucher_files', [])
        if not voucher_files:
            return jsonify({'code': 400, 'message': '凭证必填，请上传至少一张图片或PDF', 'data': None}), 400
        
        trans_no = generate_trans_no(data['trans_type'])
        
        transaction = FinanceTransaction(
            tenant_id=tenant_id,
            trans_no=trans_no,
            trans_type=data['trans_type'],
            trans_date=datetime.strptime(data['trans_date'], '%Y-%m-%d').date(),
            amount=Decimal(str(data['amount'])),
            category_id=data.get('category_id'),
            sub_category=data.get('sub_category'),
            summary=data.get('summary'),
            payment_method=data.get('payment_method'),
            voucher_files=json.dumps(voucher_files),
            source_type='manual',
            operator_id=user_id,
            status='pending'
        )
        
        # 关联字段
        if data.get('customer_id'):
            transaction.customer_id = data['customer_id']
        if data.get('employee_id'):
            transaction.employee_id = data['employee_id']
        if data.get('building_id'):
            transaction.building_id = data['building_id']
        if data.get('case_study_id'):
            transaction.case_study_id = data['case_study_id']
        if data.get('quote_id'):
            transaction.quote_id = data['quote_id']
        if data.get('contract_id'):
            transaction.contract_id = data['contract_id']
        
        db.session.add(transaction)
        db.session.commit()
        
        # 记录日志
        log_action(user_id, 'create', 'transaction', transaction.id, None, transaction.to_dict())
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': transaction.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/transactions/<int:trans_id>', methods=['PUT'])
@jwt_required()
def update_transaction(trans_id):
    """编辑流水"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'input'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        transaction = FinanceTransaction.query.get_or_404(trans_id)
        
        # 检查是否已删除
        if transaction.deleted_at:
            return jsonify({'code': 400, 'message': '该流水已删除，无法编辑', 'data': None}), 400
        
        # 记录操作前数据
        before = transaction.to_dict()
        
        data = request.get_json()
        
        # 更新字段
        if 'trans_date' in data:
            transaction.trans_date = datetime.strptime(data['trans_date'], '%Y-%m-%d').date()
        if 'amount' in data:
            transaction.amount = Decimal(str(data['amount']))
        if 'category_id' in data:
            transaction.category_id = data['category_id']
        if 'sub_category' in data:
            transaction.sub_category = data['sub_category']
        if 'summary' in data:
            transaction.summary = data['summary']
        if 'payment_method' in data:
            transaction.payment_method = data['payment_method']
        if 'voucher_files' in data:
            voucher_files = data['voucher_files']
            if not voucher_files:
                return jsonify({'code': 400, 'message': '凭证必填', 'data': None}), 400
            transaction.voucher_files = json.dumps(voucher_files)
        
        # 关联字段
        if 'customer_id' in data:
            transaction.customer_id = data['customer_id']
        if 'employee_id' in data:
            transaction.employee_id = data['employee_id']
        if 'building_id' in data:
            transaction.building_id = data['building_id']
        if 'case_study_id' in data:
            transaction.case_study_id = data['case_study_id']
        if 'quote_id' in data:
            transaction.quote_id = data['quote_id']
        if 'contract_id' in data:
            transaction.contract_id = data['contract_id']
        
        db.session.commit()
        
        # 记录日志
        log_action(user_id, 'update', 'transaction', transaction.id, before, transaction.to_dict())
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': transaction.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/transactions/<int:trans_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(trans_id):
    """删除流水"""
    try:
        user_id, tenant_id = get_current_user()
        
        transaction = FinanceTransaction.query.get_or_404(trans_id)
        
        # 检查是否已删除
        if transaction.deleted_at:
            return jsonify({'code': 400, 'message': '该流水已删除', 'data': None}), 400
        
        # 记录操作前数据
        before = transaction.to_dict()
        
        data = request.get_json() or {}
        delete_reason = data.get('reason', '')
        
        # 超级管理员直接删除
        if can_delete_directly(user_id):
            if not delete_reason:
                return jsonify({'code': 400, 'message': '请填写删除原因', 'data': None}), 400
            
            transaction.deleted_at = datetime.utcnow()
            transaction.deleted_by = user_id
            transaction.delete_reason = delete_reason
            transaction.status = 'deleted'
            
            db.session.commit()
            
            # 记录日志
            log_action(user_id, 'delete', 'transaction', transaction.id, before, transaction.to_dict())
            
            # TODO: 发送通知给所有财务人员
            
            return jsonify({
                'code': 200,
                'message': '删除成功，已通知所有财务人员',
                'data': None
            })
        
        # 普通用户检查是否已解锁
        if not is_delete_unlocked(user_id):
            return jsonify({'code': 403, 'message': '删除权限未解锁，请先提交删除申请', 'data': None}), 403
        
        # 已解锁，可以删除
        transaction.deleted_at = datetime.utcnow()
        transaction.deleted_by = user_id
        transaction.delete_reason = delete_reason
        transaction.status = 'deleted'
        
        db.session.commit()
        
        # 记录日志
        log_action(user_id, 'delete', 'transaction', transaction.id, before, transaction.to_dict())
        
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/transactions/<int:trans_id>/review', methods=['PUT'])
@jwt_required()
def review_transaction(trans_id):
    """审核流水"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'review'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        transaction = FinanceTransaction.query.get_or_404(trans_id)
        
        if transaction.status != 'pending':
            return jsonify({'code': 400, 'message': '该流水已审核', 'data': None}), 400
        
        before = transaction.to_dict()
        data = request.get_json()
        
        transaction.status = data.get('status', 'approved')
        transaction.reviewed_by = user_id
        transaction.reviewed_at = datetime.utcnow()
        
        db.session.commit()
        
        log_action(user_id, 'approve', 'transaction', transaction.id, before, transaction.to_dict())
        
        return jsonify({
            'code': 200,
            'message': '审核成功',
            'data': transaction.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/transactions/<int:trans_id>/upload-voucher', methods=['POST'])
@jwt_required()
def upload_voucher(trans_id):
    """上传凭证附件"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'input'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        transaction = FinanceTransaction.query.get_or_404(trans_id)
        
        if transaction.deleted_at:
            return jsonify({'code': 400, 'message': '该流水已删除', 'data': None}), 400
        
        file = request.files.get('file')
        if not file:
            return jsonify({'code': 400, 'message': '请选择文件', 'data': None}), 400
        
        # 生成文件名
        import os
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'pdf']:
            return jsonify({'code': 400, 'message': '仅支持 JPG/PNG/PDF 格式', 'data': None}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{transaction.trans_no}_{timestamp}.{ext}"
        
        # 保存路径（按日期分层）
        date_path = datetime.now().strftime('%Y/%m/%d')
        save_dir = os.path.join('upload', 'finance', 'vouchers', date_path)
        os.makedirs(save_dir, exist_ok=True)
        
        filepath = os.path.join(save_dir, filename)
        file.save(filepath)
        
        # 设置只读权限
        os.chmod(filepath, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # chmod 444
        
        # 更新凭证列表
        vouchers = json.loads(transaction.voucher_files) if transaction.voucher_files else []
        vouchers.append({
            'name': file.filename,
            'path': filepath,
            'size': os.path.getsize(filepath),
            'uploaded_at': datetime.now().isoformat()
        })
        transaction.voucher_files = json.dumps(vouchers)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {
                'filename': filename,
                'path': filepath,
                'vouchers': vouchers
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


# ============================================================
# 分类管理
# ============================================================

@finance_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """获取收支分类列表"""
    try:
        category_type = request.args.get('type', 'all')
        
        query = FinanceCategory.query.filter_by(is_active=True)
        
        if category_type != 'all':
            query = query.filter_by(type=category_type)
        
        categories = query.order_by(FinanceCategory.sort_order).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [cat.to_dict() for cat in categories]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """新增分类"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'settings'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        data = request.get_json()
        
        category = FinanceCategory(
            tenant_id=tenant_id,
            name=data['name'],
            type=data['type'],
            parent_id=data.get('parent_id'),
            sort_order=data.get('sort_order', 0),
            icon=data.get('icon')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': category.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


# ============================================================
# 操作日志
# ============================================================

@finance_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """获取操作日志列表"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'settings'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        action = request.args.get('action', 'all')
        target_type = request.args.get('target_type', 'all')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        query = FinanceAuditLog.query
        
        if action != 'all':
            query = query.filter_by(action=action)
        
        if target_type != 'all':
            query = query.filter_by(target_type=target_type)
        
        total = query.count()
        logs = query.order_by(FinanceAuditLog.created_at.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'items': [log.to_dict() for log in logs]
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

# ============================================================
# 报销管理
# ============================================================

@finance_bp.route('/reimbursements', methods=['GET'])
@jwt_required()
def get_reimbursements():
    """获取报销列表"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'view'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        status = request.args.get('status', 'all')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        query = FinanceReimbursement.query.filter_by(tenant_id=tenant_id)
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        total = query.count()
        reimbursements = query.order_by(FinanceReimbursement.created_at.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'items': [r.to_dict() for r in reimbursements]
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/reimbursements', methods=['POST'])
@jwt_required()
def create_reimbursement():
    """员工提交报销申请"""
    try:
        user_id, tenant_id = get_current_user()
        
        data = request.get_json()
        
        reimb_no = generate_reimb_no()
        
        reimbursement = FinanceReimbursement(
            tenant_id=tenant_id,
            reimb_no=reimb_no,
            applicant_id=user_id,
            total_amount=Decimal(str(data['total_amount'])),
            expense_date=datetime.strptime(data['expense_date'], '%Y-%m-%d').date() if data.get('expense_date') else None,
            category_id=data.get('category_id'),
            summary=data.get('summary', ''),
            detail_items=json.dumps(data.get('detail_items', [])),
            status='submitted'
        )
        
        db.session.add(reimbursement)
        db.session.commit()
        
        # 记录日志
        log_action(user_id, 'create', 'reimbursement', reimbursement.id, None, reimbursement.to_dict())
        
        return jsonify({
            'code': 200,
            'message': '报销申请已提交，请等待审核',
            'data': reimbursement.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/reimbursements/<int:reimb_id>/review', methods=['PUT'])
@jwt_required()
def review_reimbursement(reimb_id):
    """审核报销申请"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'review'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        reimbursement = FinanceReimbursement.query.get_or_404(reimb_id)
        
        if reimbursement.status != 'submitted':
            return jsonify({'code': 400, 'message': '该报销申请已审核或状态不允许操作', 'data': None}), 400
        
        before = reimbursement.to_dict()
        data = request.get_json()
        
        new_status = data.get('status', 'approved')
        reimbursement.status = new_status
        reimbursement.reviewed_by = user_id
        reimbursement.reviewed_at = datetime.utcnow()
        reimbursement.review_note = data.get('note', '')
        
        db.session.commit()
        
        log_action(user_id, 'review', 'reimbursement', reimbursement.id, before, reimbursement.to_dict())
        
        return jsonify({
            'code': 200,
            'message': '审核完成',
            'data': reimbursement.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/reimbursements/<int:reimb_id>/pay', methods=['PUT'])
@jwt_required()
def pay_reimbursement(reimb_id):
    """财务确认付款（自动生成支出流水）"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'pay'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        reimbursement = FinanceReimbursement.query.get_or_404(reimb_id)
        
        if reimbursement.status != 'approved':
            return jsonify({'code': 400, 'message': '该报销申请未审核通过', 'data': None}), 400
        
        if reimbursement.paid_at:
            return jsonify({'code': 400, 'message': '该报销已付款', 'data': None}), 400
        
        data = request.get_json()
        
        # 更新报销记录
        reimbursement.paid_by = user_id
        reimbursement.paid_at = datetime.utcnow()
        reimbursement.payment_method = data.get('payment_method', '')
        reimbursement.payment_voucher = data.get('payment_voucher', '')
        reimbursement.status = 'paid'
        
        # 自动生成支出流水
        trans_no = generate_trans_no('expense')
        transaction = FinanceTransaction(
            tenant_id=tenant_id,
            trans_no=trans_no,
            trans_type='expense',
            trans_date=datetime.utcnow().date(),
            amount=reimbursement.total_amount,
            category_id=reimbursement.category_id,
            sub_category=reimbursement.summary[:50] if reimbursement.summary else '',
            summary=f'报销付款：{reimbursement.reimb_no} - {reimbursement.summary}',
            payment_method=reimbursement.payment_method or data.get('payment_method', ''),
            voucher_files=json.dumps([reimbursement.payment_voucher]) if reimbursement.payment_voucher else '[]',
            source_type='reimbursement',
            source_id=reimbursement.id,
            operator_id=user_id,
            status='approved',
            employee_id=reimbursement.applicant_id
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        log_action(user_id, 'pay', 'reimbursement', reimbursement.id, 
                   {'status': 'approved'}, reimbursement.to_dict())
        
        return jsonify({
            'code': 200,
            'message': '付款成功，已自动生成支出流水',
            'data': {
                'reimbursement': reimbursement.to_dict(),
                'transaction': transaction.to_dict()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/my-reimbursements', methods=['GET'])
@jwt_required()
def get_my_reimbursements():
    """获取我的报销申请"""
    try:
        user_id, tenant_id = get_current_user()
        
        status = request.args.get('status', 'all')
        
        query = FinanceReimbursement.query.filter_by(applicant_id=user_id)
        
        if status != 'all':
            query = query.filter_by(status=status)
        
        reimbursements = query.order_by(FinanceReimbursement.created_at.desc()).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [r.to_dict() for r in reimbursements]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500

# ============================================================
# 投资管理
# ============================================================

@finance_bp.route('/shareholders', methods=['GET'])
@jwt_required()
def get_shareholders():
    """获取股东列表"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'view'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        shareholders = FinanceShareholder.query.filter_by(tenant_id=tenant_id).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [s.to_dict() for s in shareholders]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/shareholders', methods=['POST'])
@jwt_required()
def create_shareholder():
    """新增股东"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'settings'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        data = request.get_json()
        
        shareholder = FinanceShareholder(
            tenant_id=tenant_id,
            name=data['name'],
            id_card=data.get('id_card'),
            phone=data.get('phone'),
            share_ratio=Decimal(str(data.get('share_ratio', 0))),
            investment_amount=Decimal(str(data.get('investment_amount', 0))),
            investment_date=datetime.strptime(data['investment_date'], '%Y-%m-%d').date() if data.get('investment_date') else None,
            role=data.get('role', 'silent_investor'),
            status=data.get('status', 'active'),
            notes=data.get('notes', '')
        )
        
        db.session.add(shareholder)
        db.session.commit()
        
        log_action(user_id, 'create', 'shareholder', shareholder.id, None, shareholder.to_dict())
        
        return jsonify({
            'code': 200,
            'message': '新增成功',
            'data': shareholder.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/shareholders/<int:sh_id>', methods=['PUT'])
@jwt_required()
def update_shareholder(sh_id):
    """修改股东信息"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'settings'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        shareholder = FinanceShareholder.query.get_or_404(sh_id)
        before = shareholder.to_dict()
        data = request.get_json()
        
        shareholder.name = data.get('name', shareholder.name)
        shareholder.id_card = data.get('id_card', shareholder.id_card)
        shareholder.phone = data.get('phone', shareholder.phone)
        if 'share_ratio' in data:
            shareholder.share_ratio = Decimal(str(data['share_ratio']))
        if 'investment_amount' in data:
            shareholder.investment_amount = Decimal(str(data['investment_amount']))
        if 'investment_date' in data:
            shareholder.investment_date = datetime.strptime(data['investment_date'], '%Y-%m-%d').date() if data['investment_date'] else None
        shareholder.role = data.get('role', shareholder.role)
        shareholder.status = data.get('status', shareholder.status)
        shareholder.notes = data.get('notes', shareholder.notes)
        
        db.session.commit()
        
        log_action(user_id, 'update', 'shareholder', shareholder.id, before, shareholder.to_dict())
        
        return jsonify({
            'code': 200,
            'message': '修改成功',
            'data': shareholder.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/shareholders/<int:sh_id>', methods=['DELETE'])
@jwt_required()
def delete_shareholder(sh_id):
    """删除股东"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'settings'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        shareholder = FinanceShareholder.query.get_or_404(sh_id)
        before = shareholder.to_dict()
        
        db.session.delete(shareholder)
        db.session.commit()
        
        log_action(user_id, 'delete', 'shareholder', sh_id, before, None)
        
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/charter', methods=['GET'])
@jwt_required()
def get_charter():
    """获取企业章程"""
    try:
        user_id, tenant_id = get_current_user()
        
        charter = FinanceCharter.query.filter_by(tenant_id=tenant_id).first()
        
        if not charter:
            return jsonify({
                'code': 200,
                'message': '暂无章程',
                'data': None
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': charter.to_dict()
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/charter', methods=['POST', 'PUT'])
@jwt_required()
def save_charter():
    """保存企业章程（创建或更新）"""
    try:
        user_id, tenant_id = get_current_user()
        
        if not check_permission(user_id, 'settings'):
            return jsonify({'code': 403, 'message': '没有权限', 'data': None}), 403
        
        data = request.get_json()
        
        charter = FinanceCharter.query.filter_by(tenant_id=tenant_id).first()
        
        if charter:
            before = charter.to_dict()
            charter.title = data.get('title', charter.title)
            charter.content = data.get('content', charter.content)
            charter.version = data.get('version', charter.version)
            charter.effective_date = datetime.strptime(data['effective_date'], '%Y-%m-%d').date() if data.get('effective_date') else charter.effective_date
            charter.updated_at = datetime.utcnow()
            action = 'update'
        else:
            charter = FinanceCharter(
                tenant_id=tenant_id,
                title=data.get('title', '企业章程'),
                content=data.get('content', ''),
                version=data.get('version', '1.0'),
                effective_date=datetime.strptime(data['effective_date'], '%Y-%m-%d').date() if data.get('effective_date') else None,
                created_by=user_id
            )
            db.session.add(charter)
            before = None
            action = 'create'
        
        db.session.commit()
        
        log_action(user_id, action, 'charter', charter.id, before, charter.to_dict())
        
        return jsonify({
            'code': 200,
            'message': '保存成功',
            'data': charter.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


# ============================================================
# 财务分析
# ============================================================

@finance_bp.route('/analysis/overview', methods=['GET'])
@jwt_required()
def analysis_overview():
    """总览统计"""
    try:
        user_id, tenant_id = get_current_user()
        
        now = datetime.now()
        this_month_start = datetime(now.year, now.month, 1).date()
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        last_month_end = this_month_start - timedelta(days=1)
        
        # 本月收支
        this_month_income = db.session.query(db.func.sum(FinanceTransaction.amount)) \
            .filter(FinanceTransaction.tenant_id == tenant_id,
                    FinanceTransaction.trans_type == 'income',
                    FinanceTransaction.trans_date >= this_month_start) \
            .scalar() or Decimal('0')
        
        this_month_expense = db.session.query(db.func.sum(FinanceTransaction.amount)) \
            .filter(FinanceTransaction.tenant_id == tenant_id,
                    FinanceTransaction.trans_type == 'expense',
                    FinanceTransaction.trans_date >= this_month_start) \
            .scalar() or Decimal('0')
        
        # 上月收支
        last_month_income = db.session.query(db.func.sum(FinanceTransaction.amount)) \
            .filter(FinanceTransaction.tenant_id == tenant_id,
                    FinanceTransaction.trans_type == 'income',
                    FinanceTransaction.trans_date >= last_month_start,
                    FinanceTransaction.trans_date <= last_month_end) \
            .scalar() or Decimal('0')
        
        last_month_expense = db.session.query(db.func.sum(FinanceTransaction.amount)) \
            .filter(FinanceTransaction.tenant_id == tenant_id,
                    FinanceTransaction.trans_type == 'expense',
                    FinanceTransaction.trans_date >= last_month_start,
                    FinanceTransaction.trans_date <= last_month_end) \
            .scalar() or Decimal('0')
        
        # 总收入/总支出
        total_income = db.session.query(db.func.sum(FinanceTransaction.amount)) \
            .filter(FinanceTransaction.tenant_id == tenant_id,
                    FinanceTransaction.trans_type == 'income') \
            .scalar() or Decimal('0')
        
        total_expense = db.session.query(db.func.sum(FinanceTransaction.amount)) \
            .filter(FinanceTransaction.tenant_id == tenant_id,
                    FinanceTransaction.trans_type == 'expense') \
            .scalar() or Decimal('0')
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'this_month': {
                    'income': float(this_month_income),
                    'expense': float(this_month_expense),
                    'balance': float(this_month_income - this_month_expense)
                },
                'last_month': {
                    'income': float(last_month_income),
                    'expense': float(last_month_expense),
                    'balance': float(last_month_income - last_month_expense)
                },
                'total': {
                    'income': float(total_income),
                    'expense': float(total_expense),
                    'balance': float(total_income - total_expense)
                }
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/analysis/monthly-trend', methods=['GET'])
@jwt_required()
def analysis_monthly_trend():
    """月度收支趋势（最近12个月）"""
    try:
        user_id, tenant_id = get_current_user()
        
        months = []
        now = datetime.now()
        for i in range(11, -1, -1):
            y = now.year
            m = now.month - i
            while m <= 0:
                m += 12
                y -= 1
            months.append((y, m))
        
        result = []
        for y, m in months:
            month_start = datetime(y, m, 1).date()
            if m == 12:
                next_month = datetime(y + 1, 1, 1).date()
            else:
                next_month = datetime(y, m + 1, 1).date()
            
            income = db.session.query(db.func.sum(FinanceTransaction.amount)) \
                .filter(FinanceTransaction.tenant_id == tenant_id,
                        FinanceTransaction.trans_type == 'income',
                        FinanceTransaction.trans_date >= month_start,
                        FinanceTransaction.trans_date < next_month) \
                .scalar() or Decimal('0')
            
            expense = db.session.query(db.func.sum(FinanceTransaction.amount)) \
                .filter(FinanceTransaction.tenant_id == tenant_id,
                        FinanceTransaction.trans_type == 'expense',
                        FinanceTransaction.trans_date >= month_start,
                        FinanceTransaction.trans_date < next_month) \
                .scalar() or Decimal('0')
            
            result.append({
                'month': f'{y}-{m:02d}',
                'income': float(income),
                'expense': float(expense),
                'balance': float(income - expense)
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/analysis/category-stats', methods=['GET'])
@jwt_required()
def analysis_category_stats():
    """分类统计"""
    try:
        user_id, tenant_id = get_current_user()
        
        period = request.args.get('period', 'this_month')
        trans_type = request.args.get('trans_type', 'expense')
        
        now = datetime.now()
        if period == 'this_month':
            date_start = datetime(now.year, now.month, 1).date()
        elif period == 'last_month':
            this_month_start = datetime(now.year, now.month, 1).date()
            date_start = (this_month_start - timedelta(days=1)).replace(day=1)
        elif period == 'this_year':
            date_start = datetime(now.year, 1, 1).date()
        else:
            date_start = None
        
        query = db.session.query(
            FinanceCategory.name,
            db.func.sum(FinanceTransaction.amount).label('total')
        ).join(FinanceTransaction, FinanceTransaction.category_id == FinanceCategory.id) \
            .filter(FinanceTransaction.tenant_id == tenant_id,
                    FinanceTransaction.trans_type == trans_type)
        
        if date_start:
            query = query.filter(FinanceTransaction.trans_date >= date_start)
        
        stats = query.group_by(FinanceCategory.id).order_by(db.desc('total')).all()
        
        total = sum(float(s[1] or 0) for s in stats)
        
        # 预设颜色列表
        colors = ['#f56c6c', '#e6a23c', '#67c23a', '#409eff', '#909399', '#c456e8', '#ff9249', '#95d475']
        
        data = []
        for idx, (name, total_amount) in enumerate(stats):
            amount = float(total_amount or 0)
            data.append({
                'name': name,
                'color': colors[idx % len(colors)],
                'amount': amount,
                'percentage': round(amount / total * 100, 2) if total > 0 else 0
            })
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'items': data,
                'total': total
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/analysis/recent-transactions', methods=['GET'])
@jwt_required()
def analysis_recent_transactions():
    """最近交易记录"""
    try:
        user_id, tenant_id = get_current_user()
        
        limit = int(request.args.get('limit', 10))
        
        transactions = FinanceTransaction.query \
            .filter_by(tenant_id=tenant_id) \
            .order_by(FinanceTransaction.trans_date.desc()) \
            .limit(limit).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [t.to_dict() for t in transactions]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


# ============================================================
# 应收应付管理
# ============================================================

@finance_bp.route('/receivables', methods=['GET'])
@jwt_required()
def list_receivables():
    """获取应收款项列表"""
    try:
        user_id, tenant_id = get_current_user()
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        status = request.args.get('status')
        keyword = request.args.get('keyword', '')

        query = FinanceReceivable.query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status)
        if keyword:
            query = query.filter(FinanceReceivable.title.like(f'%{keyword}%'))
            # TODO: 如需按客户名搜索，需 JOIN customer 表

        total = query.count()
        items = query.order_by(FinanceReceivable.due_date.asc().nulls_last()).offset((page - 1) * page_size).limit(page_size).all()

        # 统计汇总
        all_items = FinanceReceivable.query.filter_by(tenant_id=tenant_id).all()
        summary = {
            'total_amount': sum(float(r.amount or 0) for r in all_items),
            'received_amount': sum(float(r.received_amount or 0) for r in all_items),
            'remaining_amount': sum(float(r.remaining_amount or 0) for r in all_items),
            'overdue_count': sum(1 for r in all_items if r.status == 'overdue'),
        }

        # 为每个 item 附加关联名称
        item_dicts = []
        for r in items:
            d = r.to_dict()
            # 补充关联名称
            if r.customer_id:
                try:
                    cust = db.session.execute(db.text('SELECT name FROM customer WHERE id = :id'), {'id': r.customer_id}).fetchone()
                    d['customer_name'] = cust[0] if cust else None
                except: d['customer_name'] = None
            if r.building_id:
                try:
                    bldg = db.session.execute(db.text('SELECT name FROM building WHERE id = :id'), {'id': r.building_id}).fetchone()
                    d['building_name'] = bldg[0] if bldg else None
                except: d['building_name'] = None
            if r.contract_id:
                try:
                    cont = db.session.execute(db.text('SELECT contract_no FROM contract WHERE id = :id'), {'id': r.contract_id}).fetchone()
                    d['contract_no'] = cont[0] if cont else None
                except: d['contract_no'] = None
            if r.quote_id:
                try:
                    qt = db.session.execute(db.text('SELECT quote_no FROM quotes WHERE id = :id'), {'id': r.quote_id}).fetchone()
                    d['quote_no'] = qt[0] if qt else None
                except: d['quote_no'] = None
            item_dicts.append(d)

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'items': item_dicts,
                'total': total,
                'summary': summary
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/receivables', methods=['POST'])
@jwt_required()
def create_receivable():
    """创建应收款项"""
    try:
        user_id, tenant_id = get_current_user()
        data = request.get_json()

        # 生成编号
        now = datetime.utcnow()
        prefix = f'AR{now.strftime("%Y%m")}'
        last = FinanceReceivable.query.filter(
            FinanceReceivable.receivable_no.like(f'{prefix}%')
        ).order_by(FinanceReceivable.id.desc()).first()
        seq = 1
        if last and last.receivable_no:
            seq = int(last.receivable_no[-4:]) + 1
        receivable_no = f'{prefix}{seq:04d}'

        amount = Decimal(str(data.get('amount', 0)))
        remaining = amount - Decimal(str(data.get('received_amount', 0)))

        item = FinanceReceivable(
            tenant_id=tenant_id,
            receivable_no=receivable_no,
            receivable_type=data.get('receivable_type', 'contract'),
            amount=amount,
            received_amount=Decimal(str(data.get('received_amount', 0))),
            remaining_amount=remaining,
            customer_id=data.get('customer_id'),
            contract_id=data.get('contract_id'),
            quote_id=data.get('quote_id'),
            building_id=data.get('building_id'),
            title=data.get('title', ''),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') and data['due_date'].strip() else None,
            status=data.get('status', 'pending'),
            remark=data.get('remark', ''),
            operator_id=user_id,
        )
        db.session.add(item)
        db.session.commit()

        log_action(user_id, 'create', 'receivable', item.id, detail_after=item.to_dict())
        return jsonify({'code': 200, 'message': '创建成功', 'data': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/receivables/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_receivable(item_id):
    """更新应收款项"""
    try:
        user_id, tenant_id = get_current_user()
        item = FinanceReceivable.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'code': 404, 'message': '记录不存在', 'data': None}), 404

        before = item.to_dict()
        data = request.get_json()

        for field in ['receivable_type', 'title', 'remark', 'status', 'customer_id',
                      'contract_id', 'quote_id', 'building_id']:
            if field in data:
                setattr(item, field, data[field])

        if 'amount' in data:
            item.amount = Decimal(str(data['amount']))
        if 'received_amount' in data:
            item.received_amount = Decimal(str(data['received_amount']))
        # 统一重算 remaining
        item.remaining_amount = item.amount - item.received_amount
        if 'due_date' in data and data['due_date'] and data['due_date'].strip():
            item.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        elif 'due_date' in data and not data.get('due_date'):
            item.due_date = None

        # 自动更新状态
        if item.remaining_amount <= 0 and item.received_amount > 0:
            item.status = 'received'
        elif item.received_amount > 0:
            item.status = 'partial'

        db.session.commit()
        log_action(user_id, 'update', 'receivable', item.id, detail_before=before, detail_after=item.to_dict())
        return jsonify({'code': 200, 'message': '更新成功', 'data': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/receivables/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_receivable(item_id):
    """删除应收款项"""
    try:
        user_id, tenant_id = get_current_user()
        item = FinanceReceivable.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'code': 404, 'message': '记录不存在', 'data': None}), 404

        before = item.to_dict()
        db.session.delete(item)
        db.session.commit()
        log_action(user_id, 'delete', 'receivable', item_id, detail_before=before)
        return jsonify({'code': 200, 'message': '删除成功', 'data': None})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/payables', methods=['GET'])
@jwt_required()
def list_payables():
    """获取应付款项列表"""
    try:
        user_id, tenant_id = get_current_user()
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        status = request.args.get('status')
        keyword = request.args.get('keyword', '')

        query = FinancePayable.query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status)
        if keyword:
            query = query.filter(
                db.or_(
                    FinancePayable.title.like(f'%{keyword}%'),
                    FinancePayable.supplier_name.like(f'%{keyword}%')
                )
            )

        total = query.count()
        items = query.order_by(FinancePayable.due_date.asc().nulls_last()).offset((page - 1) * page_size).limit(page_size).all()

        all_items = FinancePayable.query.filter_by(tenant_id=tenant_id).all()
        summary = {
            'total_amount': sum(float(p.amount or 0) for p in all_items),
            'paid_amount': sum(float(p.paid_amount or 0) for p in all_items),
            'remaining_amount': sum(float(p.remaining_amount or 0) for p in all_items),
            'overdue_count': sum(1 for p in all_items if p.status == 'overdue'),
        }

        # 为每个 item 附加关联名称
        item_dicts = []
        for p in items:
            d = p.to_dict()
            if p.building_id:
                try:
                    bldg = db.session.execute(db.text('SELECT name FROM building WHERE id = :id'), {'id': p.building_id}).fetchone()
                    d['building_name'] = bldg[0] if bldg else None
                except: d['building_name'] = None
            if p.contract_id:
                try:
                    cont = db.session.execute(db.text('SELECT contract_no FROM contract WHERE id = :id'), {'id': p.contract_id}).fetchone()
                    d['contract_no'] = cont[0] if cont else None
                except: d['contract_no'] = None
            if p.quote_id:
                try:
                    qt = db.session.execute(db.text('SELECT quote_no FROM quotes WHERE id = :id'), {'id': p.quote_id}).fetchone()
                    d['quote_no'] = qt[0] if qt else None
                except: d['quote_no'] = None
            item_dicts.append(d)

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'items': item_dicts,
                'total': total,
                'summary': summary
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/payables', methods=['POST'])
@jwt_required()
def create_payable():
    """创建应付款项"""
    try:
        user_id, tenant_id = get_current_user()
        data = request.get_json()

        now = datetime.utcnow()
        prefix = f'AP{now.strftime("%Y%m")}'
        last = FinancePayable.query.filter(
            FinancePayable.payable_no.like(f'{prefix}%')
        ).order_by(FinancePayable.id.desc()).first()
        seq = 1
        if last and last.payable_no:
            seq = int(last.payable_no[-4:]) + 1
        payable_no = f'{prefix}{seq:04d}'

        amount = Decimal(str(data.get('amount', 0)))
        remaining = amount - Decimal(str(data.get('paid_amount', 0)))

        item = FinancePayable(
            tenant_id=tenant_id,
            payable_no=payable_no,
            payable_type=data.get('payable_type', 'supplier'),
            amount=amount,
            paid_amount=Decimal(str(data.get('paid_amount', 0))),
            remaining_amount=remaining,
            supplier_name=data.get('supplier_name', ''),
            contract_id=data.get('contract_id'),
            quote_id=data.get('quote_id'),
            building_id=data.get('building_id'),
            title=data.get('title', ''),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') and data['due_date'].strip() else None,
            status=data.get('status', 'pending'),
            remark=data.get('remark', ''),
            operator_id=user_id,
        )
        db.session.add(item)
        db.session.commit()

        log_action(user_id, 'create', 'payable', item.id, detail_after=item.to_dict())
        return jsonify({'code': 200, 'message': '创建成功', 'data': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/payables/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_payable(item_id):
    """更新应付款项"""
    try:
        user_id, tenant_id = get_current_user()
        item = FinancePayable.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'code': 404, 'message': '记录不存在', 'data': None}), 404

        before = item.to_dict()
        data = request.get_json()

        for field in ['payable_type', 'title', 'remark', 'status', 'supplier_name',
                      'contract_id', 'quote_id', 'building_id']:
            if field in data:
                setattr(item, field, data[field])

        if 'amount' in data:
            item.amount = Decimal(str(data['amount']))
        if 'paid_amount' in data:
            item.paid_amount = Decimal(str(data['paid_amount']))
        # 统一重算 remaining
        item.remaining_amount = item.amount - item.paid_amount
        if 'due_date' in data and data['due_date'] and data['due_date'].strip():
            item.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        elif 'due_date' in data and not data.get('due_date'):
            item.due_date = None

        if item.remaining_amount <= 0 and item.paid_amount > 0:
            item.status = 'paid'
        elif item.paid_amount > 0:
            item.status = 'partial'

        db.session.commit()
        log_action(user_id, 'update', 'payable', item.id, detail_before=before, detail_after=item.to_dict())
        return jsonify({'code': 200, 'message': '更新成功', 'data': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/payables/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_payable(item_id):
    """删除应付款项"""
    try:
        user_id, tenant_id = get_current_user()
        item = FinancePayable.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'code': 404, 'message': '记录不存在', 'data': None}), 404

        before = item.to_dict()
        db.session.delete(item)
        db.session.commit()
        log_action(user_id, 'delete', 'payable', item_id, detail_before=before)
        return jsonify({'code': 200, 'message': '删除成功', 'data': None})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


# ============================================================
# 付款计划
# ============================================================

@finance_bp.route('/payment-plans', methods=['GET'])
@jwt_required()
def list_payment_plans():
    """获取付款计划列表"""
    try:
        user_id, tenant_id = get_current_user()
        plan_type = request.args.get('plan_type')  # receivable / payable
        parent_id = request.args.get('parent_id', type=int)
        status = request.args.get('status')

        query = FinancePaymentPlan.query.filter_by(tenant_id=tenant_id)
        if plan_type:
            query = query.filter_by(plan_type=plan_type)
        if parent_id:
            query = query.filter_by(parent_id=parent_id)
        if status:
            query = query.filter_by(status=status)

        items = query.order_by(FinancePaymentPlan.due_date.asc().nulls_last()).all()

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [p.to_dict() for p in items]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/payment-plans', methods=['POST'])
@jwt_required()
def create_payment_plan():
    """创建付款计划（支持批量创建分期）"""
    try:
        user_id, tenant_id = get_current_user()
        data = request.get_json()

        # 支持批量创建：installments = [{amount, due_date}, ...]
        installments = data.get('installments', [])
        plan_type = data.get('plan_type', 'receivable')
        parent_id = data.get('parent_id')

        if not installments:
            # 单条创建
            installments = [{
                'amount': data.get('amount', 0),
                'due_date': data.get('due_date'),
                'remark': data.get('remark', '')
            }]

        created = []
        for idx, inst in enumerate(installments, 1):
            now = datetime.utcnow()
            prefix = f'PP{now.strftime("%Y%m")}'
            last = FinancePaymentPlan.query.filter(
                FinancePaymentPlan.plan_no.like(f'{prefix}%')
            ).order_by(FinancePaymentPlan.id.desc()).first()
            seq = 1
            if last and last.plan_no:
                seq = int(last.plan_no[-4:]) + 1
            plan_no = f'{prefix}{seq:04d}'

            plan = FinancePaymentPlan(
                tenant_id=tenant_id,
                plan_no=plan_no,
                plan_type=plan_type,
                parent_id=parent_id,
                installment_no=idx,
                amount=Decimal(str(inst.get('amount', 0))),
                paid_amount=Decimal('0'),
                due_date=datetime.strptime(inst['due_date'], '%Y-%m-%d').date() if inst.get('due_date') else None,
                status='pending',
                remark=inst.get('remark', ''),
            )
            db.session.add(plan)
            created.append(plan)

        db.session.commit()

        result = [p.to_dict() for p in created]
        log_action(user_id, 'create', 'payment_plan', created[0].id if created else 0,
                   detail_after=result)
        return jsonify({'code': 200, 'message': '创建成功', 'data': result})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/payment-plans/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_payment_plan(plan_id):
    """更新付款计划（确认收款/付款）"""
    try:
        user_id, tenant_id = get_current_user()
        plan = FinancePaymentPlan.query.filter_by(id=plan_id, tenant_id=tenant_id).first()
        if not plan:
            return jsonify({'code': 404, 'message': '计划不存在', 'data': None}), 404

        before = plan.to_dict()
        data = request.get_json()

        if 'paid_amount' in data:
            plan.paid_amount = Decimal(str(data['paid_amount']))
        if 'actual_date' in data and data['actual_date']:
            plan.actual_date = datetime.strptime(data['actual_date'], '%Y-%m-%d').date()
        if 'status' in data:
            plan.status = data['status']
        if 'remark' in data:
            plan.remark = data['remark']
        if 'transaction_id' in data:
            plan.transaction_id = data['transaction_id']

        # 自动更新状态
        if plan.paid_amount >= plan.amount:
            plan.status = 'paid'
        elif plan.paid_amount > 0:
            plan.status = 'partial'

        # 同步更新父记录（应收/应付）
        if plan.plan_type == 'receivable':
            parent = FinanceReceivable.query.get(plan.parent_id)
            if parent:
                total_paid = db.session.query(
                    db.func.sum(FinancePaymentPlan.paid_amount)
                ).filter_by(plan_type='receivable', parent_id=parent.id).scalar() or 0
                parent.received_amount = total_paid
                parent.remaining_amount = parent.amount - total_paid
                if parent.remaining_amount <= 0:
                    parent.status = 'received'
                elif parent.received_amount > 0:
                    parent.status = 'partial'
        elif plan.plan_type == 'payable':
            parent = FinancePayable.query.get(plan.parent_id)
            if parent:
                total_paid = db.session.query(
                    db.func.sum(FinancePaymentPlan.paid_amount)
                ).filter_by(plan_type='payable', parent_id=parent.id).scalar() or 0
                parent.paid_amount = total_paid
                parent.remaining_amount = parent.amount - total_paid
                if parent.remaining_amount <= 0:
                    parent.status = 'paid'
                elif parent.paid_amount > 0:
                    parent.status = 'partial'

        # 确认收付款时自动创建流水记录
        if data.get('status') in ('paid',) or (plan.status == 'paid' and 'paid_amount' in data):
            # 检查是否已有对应流水（避免重复）
            existing_tx = FinanceTransaction.query.filter_by(
                tenant_id=tenant_id,
                source_type='payment_plan',
                source_id=plan.id
            ).first()
            if not existing_tx:
                # 确定流水类型和分类
                if plan.plan_type == 'receivable':
                    trans_type = 'income'
                    cat_name = '应收回款'
                else:
                    trans_type = 'expense'
                    cat_name = '应付付款'
                # 查找或创建分类
                cat = FinanceCategory.query.filter_by(
                    tenant_id=tenant_id, name=cat_name, type=trans_type
                ).first()
                if not cat:
                    cat = FinanceCategory(
                        tenant_id=tenant_id, name=cat_name, type=trans_type,
                        is_active=True
                    )
                    db.session.add(cat)
                    db.session.flush()
                # 生成流水编号
                today_str = datetime.utcnow().strftime('%Y%m')
                prefix = f'TX{today_str}'
                last_tx = FinanceTransaction.query.filter(
                    FinanceTransaction.trans_no.like(f'{prefix}%')
                ).order_by(FinanceTransaction.id.desc()).first()
                seq = 1
                if last_tx and last_tx.trans_no:
                    seq = int(last_tx.trans_no[-4:]) + 1
                trans_no = f'{prefix}{seq:04d}'
                # 创建流水
                tx = FinanceTransaction(
                    tenant_id=tenant_id,
                    trans_no=trans_no,
                    trans_type=trans_type,
                    category_id=cat.id,
                    amount=float(plan.paid_amount or 0),
                    summary=f'[自动] {plan.plan_no} 确认{"收款" if plan.plan_type == "receivable" else "付款"}',
                    trans_date=plan.actual_date or datetime.utcnow().date(),
                    status='approved',
                    operator_id=user_id,
                    source_type='payment_plan',
                    source_id=plan.id
                )
                db.session.add(tx)
                db.session.flush()
                plan.transaction_id = tx.id

        db.session.commit()
        log_action(user_id, 'update', 'payment_plan', plan.id,
                   detail_before=before, detail_after=plan.to_dict())
        return jsonify({'code': 200, 'message': '更新成功', 'data': plan.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/payment-plans/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_payment_plan(plan_id):
    """删除付款计划"""
    try:
        user_id, tenant_id = get_current_user()
        plan = FinancePaymentPlan.query.filter_by(id=plan_id, tenant_id=tenant_id).first()
        if not plan:
            return jsonify({'code': 404, 'message': '计划不存在', 'data': None}), 404

        before = plan.to_dict()
        db.session.delete(plan)
        db.session.commit()
        log_action(user_id, 'delete', 'payment_plan', plan_id, detail_before=before)
        return jsonify({'code': 200, 'message': '删除成功', 'data': None})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


# ============================================================
# 部门管理
# ============================================================

@finance_bp.route('/departments', methods=['GET'])
@jwt_required()
def list_departments():
    """获取部门列表"""
    try:
        user_id, tenant_id = get_current_user()
        keyword = request.args.get('keyword', '')
        query = FinanceDepartment.query.filter_by(tenant_id=tenant_id)
        if keyword:
            query = query.filter(FinanceDepartment.name.like(f'%{keyword}%'))
        items = query.order_by(FinanceDepartment.sort_order, FinanceDepartment.id).all()
        return jsonify({'code': 200, 'message': '获取成功', 'data': [i.to_dict() for i in items]})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/departments', methods=['POST'])
@jwt_required()
def create_department():
    """创建部门"""
    try:
        user_id, tenant_id = get_current_user()
        data = request.get_json()
        item = FinanceDepartment(
            tenant_id=tenant_id,
            dept_code=data.get('dept_code', ''),
            name=data.get('name'),
            parent_id=data.get('parent_id'),
            leader_id=data.get('leader_id'),
            leader_name=data.get('leader_name', ''),
            description=data.get('description', ''),
            sort_order=data.get('sort_order', 0),
            status=data.get('status', 'active'),
        )
        db.session.add(item)
        db.session.commit()
        log_action(user_id, 'create', 'department', item.id, detail_after=item.to_dict())
        return jsonify({'code': 200, 'message': '创建成功', 'data': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/departments/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_department(item_id):
    """更新部门"""
    try:
        user_id, tenant_id = get_current_user()
        item = FinanceDepartment.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'code': 404, 'message': '部门不存在', 'data': None}), 404
        before = item.to_dict()
        data = request.get_json()
        for field in ['dept_code', 'name', 'parent_id', 'leader_id', 'leader_name', 'description', 'sort_order', 'status']:
            if field in data:
                setattr(item, field, data[field])
        db.session.commit()
        log_action(user_id, 'update', 'department', item.id, detail_before=before, detail_after=item.to_dict())
        return jsonify({'code': 200, 'message': '更新成功', 'data': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/departments/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_department(item_id):
    """删除部门"""
    try:
        user_id, tenant_id = get_current_user()
        item = FinanceDepartment.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'code': 404, 'message': '部门不存在', 'data': None}), 404
        before = item.to_dict()
        db.session.delete(item)
        db.session.commit()
        log_action(user_id, 'delete', 'department', item_id, detail_before=before)
        return jsonify({'code': 200, 'message': '删除成功', 'data': None})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


# ============================================================
# 岗位管理
# ============================================================

@finance_bp.route('/positions', methods=['GET'])
@jwt_required()
def list_positions():
    """获取岗位列表"""
    try:
        user_id, tenant_id = get_current_user()
        keyword = request.args.get('keyword', '')
        dept_id = request.args.get('dept_id')
        query = FinancePosition.query.filter_by(tenant_id=tenant_id)
        if keyword:
            query = query.filter(FinancePosition.name.like(f'%{keyword}%'))
        if dept_id:
            query = query.filter_by(dept_id=int(dept_id))
        items = query.order_by(FinancePosition.sort_order, FinancePosition.id).all()
        # 附加部门名称
        result = []
        for p in items:
            d = p.to_dict()
            if p.dept_id:
                dept = FinanceDepartment.query.get(p.dept_id)
                d['dept_name'] = dept.name if dept else None
            result.append(d)
        return jsonify({'code': 200, 'message': '获取成功', 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/positions', methods=['POST'])
@jwt_required()
def create_position():
    """创建岗位"""
    try:
        user_id, tenant_id = get_current_user()
        data = request.get_json()
        item = FinancePosition(
            tenant_id=tenant_id,
            position_code=data.get('position_code', ''),
            name=data.get('name'),
            dept_id=data.get('dept_id'),
            level=data.get('level', ''),
            responsibilities=data.get('responsibilities', ''),
            sort_order=data.get('sort_order', 0),
            status=data.get('status', 'active'),
        )
        db.session.add(item)
        db.session.commit()
        log_action(user_id, 'create', 'position', item.id, detail_after=item.to_dict())
        return jsonify({'code': 200, 'message': '创建成功', 'data': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/positions/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_position(item_id):
    """更新岗位"""
    try:
        user_id, tenant_id = get_current_user()
        item = FinancePosition.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'code': 404, 'message': '岗位不存在', 'data': None}), 404
        before = item.to_dict()
        data = request.get_json()
        for field in ['position_code', 'name', 'dept_id', 'level', 'responsibilities', 'sort_order', 'status']:
            if field in data:
                setattr(item, field, data[field])
        db.session.commit()
        log_action(user_id, 'update', 'position', item.id, detail_before=before, detail_after=item.to_dict())
        return jsonify({'code': 200, 'message': '更新成功', 'data': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500


@finance_bp.route('/positions/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_position(item_id):
    """删除岗位"""
    try:
        user_id, tenant_id = get_current_user()
        item = FinancePosition.query.filter_by(id=item_id, tenant_id=tenant_id).first()
        if not item:
            return jsonify({'code': 404, 'message': '岗位不存在', 'data': None}), 404
        before = item.to_dict()
        db.session.delete(item)
        db.session.commit()
        log_action(user_id, 'delete', 'position', item_id, detail_before=before)
        return jsonify({'code': 200, 'message': '删除成功', 'data': None})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e), 'data': None}), 500
