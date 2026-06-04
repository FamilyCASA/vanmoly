"""
数据库迁移：给所有缺少 tenant_id 的表添加字段
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

app = create_app()

# 需要添加 tenant_id 的表（排除已有字段的）
ADD_TENANT = [
    'building_customer', 'building_follow', 'career_path',
    'case_files', 'case_leads', 'case_media', 'case_notifications',
    'case_operation_logs', 'case_subscriptions', 'case_templates',
    'case_timeline', 'contract_change', 'contract_payment',
    'coupon_claim', 'customer_follow', 'customer_schemes',
    'digital_asset_transfers', 'employee_contract',
    'employee_performance', 'employee_points', 'employee_salary',
    'employee_welfare', 'lead_distribution', 'lead_follow',
    'lead_point', 'login_logs', 'material_variant',
    'performance_review', 'points_transaction', 'quote_item',
    'quote_template', 'scheme_items', 'training_record',
    'workflow_node', 'workflow_node_record',
    # 已检查到这些表有tenant_id，但确保字段存在
    'appointment', 'article', 'building', 'case_study',
    'contract', 'contract_template', 'coupon', 'customer',
    'customer_workflow', 'department', 'lead', 'material_category',
    'material_sku', 'material_supplier', 'position', 'quote',
    'sales_material', 'stores', 'users_v2',
]

with app.app_context():
    inspector = db.inspect(db.engine)
    existing = set(inspector.get_table_names())

    for tbl in ADD_TENANT:
        if tbl not in existing:
            print(f'SKIP: {tbl} does not exist')
            continue
        cols = {c['name'] for c in inspector.get_columns(tbl)}
        if 'tenant_id' in cols:
            print(f'SKIP: {tbl} already has tenant_id')
            continue
        try:
            db.session.execute(text(f"ALTER TABLE {tbl} ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default'"))
            db.session.commit()
            print(f'OK: {tbl} + tenant_id')
        except Exception as e:
            print(f'FAIL: {tbl} -> {e}')
            db.session.rollback()

print('Done.')