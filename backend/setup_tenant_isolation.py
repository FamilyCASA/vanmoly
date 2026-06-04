import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # 1. 给 employee/lead/customer 添加 store_id 字段
    for tbl, has in [('employee', False), ('lead', False), ('customer', False)]:
        cols = {c['name'] for c in db.inspect(db.engine).get_columns(tbl)}
        if 'store_id' not in cols:
            db.session.execute(text(f'ALTER TABLE {tbl} ADD COLUMN store_id INTEGER'))
            print(f'OK: {tbl} + store_id')
        else:
            print(f'SKIP: {tbl} already has store_id')
    db.session.commit()

    # 2. 获取 stores 数据
    stores = db.session.execute(text('SELECT id, tenant_id, code FROM stores')).fetchall()
    store_map = {s[2]: s[0] for s in stores}  # code -> id
    store_tenant = {s[0]: s[1] for s in stores}  # id -> tenant_id
    print(f'Stores: {stores}')

    # 3. 分配门店
    # - 总部员工 (前15个): store_id = 1 (HQ)
    # - 门店A员工 (中间12个): store_id = 2
    # - 门店B员工 (后面13个): store_id = 3
    # - 所有现有员工 tenant_id = 'hq'
    emps = db.session.execute(text('SELECT id FROM employee ORDER BY id')).fetchall()
    emp_ids = [e[0] for e in emps]
    n = len(emp_ids)
    store_assignments = []
    for i, eid in enumerate(emp_ids):
        if i < 15:
            sid, tid = 1, 'hq'
        elif i < 27:
            sid, tid = 2, 'store_001'
        else:
            sid, tid = 3, 'store_002'
        db.session.execute(text(
            "UPDATE employee SET store_id = :sid, tenant_id = :tid WHERE id = :eid"
        ), {'sid': sid, 'tid': tid, 'eid': eid})
        store_assignments.append((eid, sid, tid))
    
    db.session.commit()

    # 4. 为线索和客户分配 store_id
    # 现有10条线索全部分给 HQ
    db.session.execute(text("UPDATE lead SET store_id = 1 WHERE store_id IS NULL"))
    db.session.execute(text("UPDATE customer SET store_id = 1 WHERE store_id IS NULL"))
    db.session.commit()

    # 5. 创建 tenant_user 关联（员工-租户关系）
    existing_tu = db.session.execute(text('SELECT COUNT(*) FROM tenant_user')).fetchone()[0]
    if existing_tu == 0:
        for eid, sid, tid in store_assignments:
            db.session.execute(text(
                "INSERT INTO tenant_user (tenant_id, employee_id, role, is_active) VALUES (:tid, :eid, :role, 1)"
            ), {'tid': tid, 'eid': eid, 'role': 'admin'})
        db.session.commit()
        print(f'OK: {len(store_assignments)} tenant_user records created')

    # 6. 验证
    print('\n=== 验证 ===')
    r1 = db.session.execute(text('SELECT tenant_id, store_id, COUNT(*) FROM employee GROUP BY tenant_id, store_id')).fetchall()
    print('employee distribution:', r1)
    r2 = db.session.execute(text('SELECT COUNT(*), tenant_id FROM tenant_user GROUP BY tenant_id')).fetchall()
    print('tenant_user distribution:', r2)
    r3 = db.session.execute(text('SELECT COUNT(*), store_id FROM lead GROUP BY store_id')).fetchall()
    print('lead by store:', r3)
    
    print('\nDone. Multi-tenant isolation configured.')
    print('Summary:')
    print('  - hq: store_id=1, 15 employees')
    print('  - store_001: store_id=2, 12 employees')
    print('  - store_002: store_id=3, 13 employees')
    print('  - leads and customers all assigned to hq (store_id=1)')