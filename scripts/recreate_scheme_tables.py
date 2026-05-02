"""
重新创建客户方案相关数据表（结构调整后）
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db
from app.models.scheme import CustomerScheme, SchemeItem
from sqlalchemy import inspect, text

def recreate_tables():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # 删除旧表（如果存在）
        if 'scheme_items' in existing_tables:
            print("Dropping table: scheme_items")
            db.session.execute(text("DROP TABLE scheme_items"))
            db.session.commit()
            
        if 'customer_schemes' in existing_tables:
            print("Dropping table: customer_schemes")
            db.session.execute(text("DROP TABLE customer_schemes"))
            db.session.commit()
        
        # 创建新表
        print("Creating table: customer_schemes")
        CustomerScheme.__table__.create(db.engine)
        
        print("Creating table: scheme_items")
        SchemeItem.__table__.create(db.engine)
        
        # 验证
        inspector = inspect(db.engine)
        scheme_tables = [t for t in inspector.get_table_names() if 'scheme' in t]
        print(f"\nScheme tables: {scheme_tables}")
        
        # 打印表结构
        for table_name in scheme_tables:
            columns = inspector.get_columns(table_name)
            print(f"\n{table_name} columns:")
            for col in columns[:5]:  # 只显示前5列
                print(f"  - {col['name']}: {col['type']}")
            if len(columns) > 5:
                print(f"  ... and {len(columns)-5} more columns")

if __name__ == '__main__':
    recreate_tables()
