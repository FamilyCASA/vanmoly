"""诊断数据库表结构"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print('=== Main database tables ===')
    for t in sorted(tables):
        cols = [c['name'] for c in inspector.get_columns(t)]
        org_cols = [c for c in cols if any(k in c.lower() for k in ['org_id', 'tenant', 'store', 'branch', 'source', 'is_head'])]
        print(f'{t}: org_cols={org_cols}')
    
    # Check material db
    import os
    mat_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'material.db')
    if os.path.exists(mat_db):
        from sqlalchemy import create_engine
        mat_inspector = inspect(create_engine(f'sqlite:///{mat_db}'))
        mat_tables = mat_inspector.get_table_names()
        print(f'\n=== material.db tables ===')
        for t in sorted(mat_tables):
            cols = [c['name'] for c in mat_inspector.get_columns(t)]
            org_cols = [c for c in cols if any(k in c.lower() for k in ['org_id', 'tenant', 'store', 'branch', 'source'])]
            print(f'{t}: org_cols={org_cols}')