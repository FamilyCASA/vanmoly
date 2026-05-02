"""快速检查模型是否可导入"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 只导入 app，不启动 server
from app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    # 检查所有表
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'OK: {len(tables)} tables in main db')
    for t in sorted(tables):
        print(f'  - {t}')