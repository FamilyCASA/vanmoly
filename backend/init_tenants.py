"""
初始化租户/门店数据 + 迁移员工关联
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text
from datetime import datetime

app = create_app()

with app.app_context():
    # 1. 创建租户数据（如果不存在）
    tenants = [
        {'id': 'hq', 'name': 'D&B 帝标|设记家总部', 'type': 'hq', 'parent_id': None,
         'store_code': 'HQ001', 'address': '成都市高新区', 'phone': '028-88888888'},
        {'id': 'store_001', 'name': 'D&B 帝标|设记家锦江店', 'type': 'store', 'parent_id': 'hq',
         'store_code': 'SJ001', 'address': '成都市锦江区', 'phone': '028-88888801'},
        {'id': 'store_002', 'name': 'D&B 帝标|设记家武侯店', 'type': 'store', 'parent_id': 'hq',
         'store_code': 'WH001', 'address': '成都市武侯区', 'phone': '028-88888802'},
    ]

    existing_stores = db.session.execute(text('SELECT code FROM stores')).fetchall()
    existing_codes = {row[0] for row in existing_stores}

    for t in tenants:
        if t['store_code'] in existing_codes:
            print(f'SKIP store: {t["store_code"]}')
        else:
            db.session.execute(text("""
                INSERT INTO stores (code, name, address, phone, status, tenant_id)
                VALUES (:code, :name, :address, :phone, 'active', :tenant_id)
            """), {'code': t['store_code'], 'name': t['name'],
                   'address': t.get('address', ''), 'phone': t.get('phone', ''),
                   'tenant_id': t['id']})
            print(f'OK: store {t["name"]} ({t["store_code"]})')

    db.session.commit()

    # 2. 确保 tenant 表已创建（如果不存在则创建）
    inspector = db.inspect(db.engine)
    if 'tenant' not in inspector.get_table_names():
        db.session.execute(text('''
            CREATE TABLE tenant (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(20) DEFAULT 'store',
                parent_id VARCHAR(50),
                store_code VARCHAR(50) UNIQUE,
                address VARCHAR(255),
                phone VARCHAR(20),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        db.session.commit()
        print('OK: tenant table created')
    else:
        print('SKIP: tenant table exists')

    # 3. 确保 tenant_user 表已创建
    if 'tenant_user' not in inspector.get_table_names():
        db.session.execute(text('''
            CREATE TABLE tenant_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(50) NOT NULL,
                employee_id INTEGER NOT NULL,
                role VARCHAR(20) DEFAULT 'employee',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenant(id),
                FOREIGN KEY (employee_id) REFERENCES employee(id)
            )
        '''))
        db.session.commit()
        print('OK: tenant_user table created')
    else:
        print('SKIP: tenant_user table exists')

    # 4. 将所有现有员工标记为 HQ 员工（tenant_id = 'hq'）
    result = db.session.execute(text("SELECT COUNT(*) FROM employee WHERE tenant_id IS NULL OR tenant_id = ''"))
    count = result.fetchone()[0]
    if count > 0:
        db.session.execute(text("UPDATE employee SET tenant_id = 'hq' WHERE tenant_id IS NULL OR tenant_id = ''"))
        db.session.commit()
        print(f'OK: {count} employees marked as hq')
    else:
        print('SKIP: all employees already have tenant_id')

    # 5. 创建 TenantUser 关联（所有现有员工 -> hq）
    result2 = db.session.execute(text("SELECT COUNT(*) FROM tenant_user WHERE tenant_id = 'hq'"))
    count2 = result2.fetchone()[0]
    if count2 == 0:
        employees = db.session.execute(text('SELECT id FROM employee WHERE tenant_id = "hq"')).fetchall()
        for emp in employees:
            db.session.execute(text("""
                INSERT INTO tenant_user (tenant_id, employee_id, role) VALUES ('hq', :eid, 'admin')
            """), {'eid': emp[0]})
        db.session.commit()
        print(f'OK: {len(employees)} tenant_user records created for hq')
    else:
        print(f'SKIP: {count2} tenant_user records already exist')

    # 6. 将所有现有客户和线索标记为 hq（暂时）
    for tbl, col in [('customer', 'tenant_id'), ('lead', 'tenant_id')]:
        result3 = db.session.execute(text(f"SELECT COUNT(*) FROM {tbl} WHERE {col} IS NULL OR {col} = ''"))
        count3 = result3.fetchone()[0]
        if count3 > 0:
            db.session.execute(text(f"UPDATE {tbl} SET {col} = 'hq' WHERE {col} IS NULL OR {col} = ''"))
            db.session.commit()
            print(f'OK: {count3} {tbl} records marked as hq')
        else:
            print(f'SKIP: all {tbl} already have tenant_id')

    # 7. 验证
    print('\n=== 数据验证 ===')
    r1 = db.session.execute(text('SELECT COUNT(*), tenant_id FROM employee GROUP BY tenant_id')).fetchall()
    print('employee by tenant:', r1)
    r2 = db.session.execute(text('SELECT COUNT(*), tenant_id FROM customer GROUP BY tenant_id')).fetchall()
    print('customer by tenant:', r2)
    r3 = db.session.execute(text('SELECT COUNT(*), tenant_id FROM lead GROUP BY tenant_id')).fetchall()
    print('lead by tenant:', r3)

    print('\nDone. Tenant isolation initialized.')