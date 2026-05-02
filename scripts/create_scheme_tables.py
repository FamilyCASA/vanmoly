"""
创建客户方案相关数据表
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db
from app.models.scheme import CustomerScheme, SchemeItem
from sqlalchemy import inspect

def create_tables():
    app = create_app()
    with app.app_context():
        # 检查表是否已存在
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"现有表: {existing_tables}")
        
        # 创建方案相关表
        tables_to_create = []
        if 'customer_schemes' not in existing_tables:
            tables_to_create.append(CustomerScheme.__table__)
            print("将创建表: customer_schemes")
        else:
            print("表已存在: customer_schemes")
            
        if 'scheme_items' not in existing_tables:
            tables_to_create.append(SchemeItem.__table__)
            print("将创建表: scheme_items")
        else:
            print("表已存在: scheme_items")
        
        if tables_to_create:
            # 创建表
            for table in tables_to_create:
                table.create(db.engine, checkfirst=True)
            print("\n✅ 表创建完成!")
        else:
            print("\n✅ 所有表已存在，无需创建")
        
        # 验证
        inspector = inspect(db.engine)
        print(f"\n当前数据库表列表: {inspector.get_table_names()}")

if __name__ == '__main__':
    create_tables()
