import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'Tables: {len(tables)}')
    for t in sorted(tables):
        cols = [c['name'] for c in inspector.get_columns(t)]
        org = [c for c in cols if c.lower() in ['org_id', 'tenant_id', 'store_id', 'branch_id', 'is_head_office']]
        tag = ', '.join(org) if org else 'NO_ORG_FIELD'
        print(f'{t}: {tag}')