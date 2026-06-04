import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    inspector = db.inspect(db.engine)
    cols = [c['name'] for c in inspector.get_columns('tenant')]
    print('tenant columns:', cols)
    
    # 插入租户数据
    tenants = [
        ('hq', 'Vanmoli HQ', 'hq', None),
        ('store_001', 'Jinjiang Store', 'store', 'hq'),
        ('store_002', 'Wuhou Store', 'store', 'hq'),
    ]
    for t in tenants:
        try:
            db.session.execute(text(
                "INSERT OR IGNORE INTO tenant (id, name, type, parent_id) VALUES (:id, :name, :type, :pid)"
            ), {'id': t[0], 'name': t[1], 'type': t[2], 'pid': t[3]})
        except Exception as e:
            print(f'insert tenant {t[0]} failed: {e}')
    db.session.commit()
    
    r = db.session.execute(text('SELECT id, name, type, parent_id FROM tenant')).fetchall()
    print('tenants:', r)
    
    # 检查 stores 表的 tenant_id 映射
    r2 = db.session.execute(text('SELECT id, code, name, tenant_id FROM stores')).fetchall()
    print('stores:', r2)
    
    print('Done.')