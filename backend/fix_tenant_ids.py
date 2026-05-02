import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # 检查 employee tenant_id 的实际情况
    r = db.session.execute(text('SELECT DISTINCT tenant_id FROM employee LIMIT 10')).fetchall()
    print('employee tenant_ids:', r)
    r2 = db.session.execute(text('SELECT DISTINCT tenant_id FROM customer LIMIT 10')).fetchall()
    print('customer tenant_ids:', r2)
    
    # 统一设置为 hq
    db.session.execute(text("UPDATE employee SET tenant_id = 'hq' WHERE tenant_id IS NULL OR tenant_id = '' OR tenant_id = '0' OR tenant_id = 'default'"))
    db.session.execute(text("UPDATE customer SET tenant_id = 'hq' WHERE tenant_id IS NULL OR tenant_id = '' OR tenant_id = '0' OR tenant_id = 'default'"))
    db.session.commit()
    
    r3 = db.session.execute(text('SELECT tenant_id, COUNT(*) FROM employee GROUP BY tenant_id')).fetchall()
    print('employee after fix:', r3)
    r4 = db.session.execute(text('SELECT tenant_id, COUNT(*) FROM customer GROUP BY tenant_id')).fetchall()
    print('customer after fix:', r4)
    
    # 确认 tenant 表有数据
    r5 = db.session.execute(text('SELECT id, name, type FROM tenant')).fetchall()
    print('tenants:', r5)
    
    print('Done.')