# -*- coding: utf-8 -*-
"""
财务管理模块数据库初始化脚本

功能：
1. 创建所有财务相关表
2. 插入预置财务角色种子数据
3. 插入预置收支分类种子数据
4. 创建凭证存储目录
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import db, create_app
from app.models.finance import (
    FinanceRole, FinanceMember, FinanceApprovalFlow, FinanceDeleteRequest,
    FinanceTransaction, FinanceCategory, FinanceReimbursement,
    FinanceShareholder, FinanceCharter, FinanceAuditLog
)
import json


def create_voucher_directories():
    """创建凭证存储目录"""
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'upload', 'finance', 'vouchers')
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backup', 'finance', 'vouchers')
    
    # 创建主存储目录（按年月日分层）
    today = datetime.now()
    year_month_day = today.strftime('%Y/%m/%d')
    voucher_dir = os.path.join(base_dir, year_month_day)
    backup_voucher_dir = os.path.join(backup_dir, year_month_day)
    
    os.makedirs(voucher_dir, exist_ok=True)
    os.makedirs(backup_voucher_dir, exist_ok=True)
    
    print(f"✅ 凭证存储目录已创建: {voucher_dir}")
    print(f"✅ 凭证备份目录已创建: {backup_voucher_dir}")
    
    return voucher_dir


def seed_finance_roles():
    """插入财务角色种子数据"""
    roles_data = [
        {
            'role_code': 'finance_super_admin',
            'role_name': '超级管理员',
            'permissions': ['view', 'input', 'review', 'pay', 'export', 'settings', 'delete'],
            'can_delete': True,
            'delete_approval_required': False,
            'description': '全部权限（设置/查看/录入/审核/付款），可直接删除流水',
            'is_system': True
        },
        {
            'role_code': 'finance_manager',
            'role_name': '财务主管',
            'permissions': ['view', 'input', 'review', 'pay', 'export'],
            'can_delete': False,
            'delete_approval_required': True,
            'description': '查看+录入+审核+付款，删除需审批',
            'is_system': True
        },
        {
            'role_code': 'finance_clerk',
            'role_name': '财务专员',
            'permissions': ['view', 'input'],
            'can_delete': False,
            'delete_approval_required': True,
            'description': '查看+录入流水，删除需审批',
            'is_system': True
        },
        {
            'role_code': 'dept_head',
            'role_name': '部门负责人',
            'permissions': ['view', 'review'],
            'can_delete': False,
            'delete_approval_required': True,
            'description': '查看本部门数据 + 审核本部门报销',
            'is_system': True
        },
        {
            'role_code': 'employee',
            'role_name': '普通员工',
            'permissions': ['view'],
            'can_delete': False,
            'delete_approval_required': True,
            'description': '仅提交个人报销 + 查看自己相关流水',
            'is_system': True
        }
    ]
    
    created_count = 0
    for role_data in roles_data:
        # 检查是否已存在
        existing = FinanceRole.query.filter_by(role_code=role_data['role_code']).first()
        if not existing:
            role = FinanceRole(
                tenant_id='default',
                role_code=role_data['role_code'],
                role_name=role_data['role_name'],
                permissions=json.dumps(role_data['permissions']),
                can_delete=role_data['can_delete'],
                delete_approval_required=role_data['delete_approval_required'],
                description=role_data['description'],
                is_system=role_data['is_system']
            )
            db.session.add(role)
            created_count += 1
    
    db.session.commit()
    print(f"✅ 已插入 {created_count} 个财务角色")


def seed_finance_categories():
    """插入收支分类种子数据"""
    categories_data = [
        # 支出类
        {'name': '主材支出', 'type': 'expense', 'icon': 'material'},
        {'name': '工资支出', 'type': 'expense', 'icon': 'salary'},
        {'name': '差旅支出', 'type': 'expense', 'icon': 'travel'},
        {'name': '施工支出', 'type': 'expense', 'icon': 'construction'},
        {'name': '设计费支出', 'type': 'expense', 'icon': 'design'},
        {'name': '销售提成支出', 'type': 'expense', 'icon': 'commission'},
        {'name': '推广支出', 'type': 'expense', 'icon': 'marketing'},
        {'name': '人力成本', 'type': 'expense', 'icon': 'hr'},
        {'name': '分红支出', 'type': 'expense', 'icon': 'dividend'},
        {'name': '其他支出', 'type': 'expense', 'icon': 'other'},
        
        # 收入类
        {'name': '设计收入', 'type': 'income', 'icon': 'design_income'},
        {'name': '全案服务收入', 'type': 'income', 'icon': 'full_service'},
        {'name': '施工服务收入', 'type': 'income', 'icon': 'construction_income'},
        {'name': '成品家具销售', 'type': 'income', 'icon': 'furniture'},
        {'name': '定制家具销售', 'type': 'income', 'icon': 'custom_furniture'},
        {'name': '软装饰品销售', 'type': 'income', 'icon': 'decoration'},
        {'name': '培训赋能收入', 'type': 'income', 'icon': 'training'},
        {'name': '其他收入', 'type': 'income', 'icon': 'other_income'},
    ]
    
    # 二级分类
    sub_categories = {
        '施工支出': ['木工', '油工', '瓦工', '水电', '泥工'],
        '推广支出': ['线下推广', '线上流量', '新媒体运营'],
        '人力成本': ['福利支出', '团建支出'],
    }
    
    created_count = 0
    for idx, cat_data in enumerate(categories_data):
        # 检查是否已存在
        existing = FinanceCategory.query.filter_by(name=cat_data['name'], type=cat_data['type']).first()
        if not existing:
            parent = FinanceCategory(
                tenant_id='default',
                name=cat_data['name'],
                type=cat_data['type'],
                icon=cat_data['icon'],
                sort_order=idx,
                is_active=True
            )
            db.session.add(parent)
            db.session.flush()  # 获取 parent.id
            
            # 添加二级分类
            if cat_data['name'] in sub_categories:
                for sub_idx, sub_name in enumerate(sub_categories[cat_data['name']]):
                    sub = FinanceCategory(
                        tenant_id='default',
                        name=sub_name,
                        type=cat_data['type'],
                        parent_id=parent.id,
                        sort_order=sub_idx,
                        is_active=True
                    )
                    db.session.add(sub)
            
            created_count += 1
    
    db.session.commit()
    print(f"✅ 已插入 {created_count} 个收支分类（含二级分类）")


def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("开始初始化财务管理模块数据库...")
        print("=" * 60)
        
        # 创建所有表
        print("\n📊 创建数据库表...")
        db.create_all()
        print("✅ 所有表已创建")
        
        # 创建凭证目录
        print("\n📁 创建凭证存储目录...")
        create_voucher_directories()
        
        # 插入种子数据
        print("\n🌱 插入种子数据...")
        seed_finance_roles()
        seed_finance_categories()
        
        print("\n" + "=" * 60)
        print("✅ 财务管理模块初始化完成！")
        print("=" * 60)
        print("\n📋 已创建表:")
        tables = [
            'finance_role', 'finance_member', 'finance_approval_flow', 'finance_delete_request',
            'finance_transaction', 'finance_category', 'finance_reimbursement',
            'finance_shareholder', 'finance_charter', 'finance_audit_log'
        ]
        for table in tables:
            print(f"  - {table}")
        
        print("\n📌 下一步:")
        print("  1. 重启后端服务")
        print("  2. 开发财务路由 API")
        print("  3. 开发前端页面")


if __name__ == '__main__':
    init_database()
