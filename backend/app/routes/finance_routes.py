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
    FinanceShareholder, FinanceCharter, FinanceAuditLog
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
            address=data.get('address'),
            investment_ratio=Decimal(str(data.get('investment_ratio', 0))),
            investment_amount=Decimal(str(data.get('investment_amount', 0)))
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
        shareholder.address = data.get('address', shareholder.address)
        if 'investment_ratio' in data:
            shareholder.investment_ratio = Decimal(str(data['investment_ratio']))
        if 'investment_amount' in data:
            shareholder.investment_amount = Decimal(str(data['investment_amount']))
        
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
            # 更新
            before = charter.to_dict()
            charter.content = data.get('content', charter.content)
            charter.version = data.get('version', charter.version)
            charter.updated_by = user_id
            charter.updated_at = datetime.utcnow()
            action = 'update'
        else:
            # 创建
            charter = FinanceCharter(
                tenant_id=tenant_id,
                content=data['content'],
                version=data.get('version', '1.0'),
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
