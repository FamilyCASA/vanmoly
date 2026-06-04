"""
数据库迁移脚本：为quote表添加报价升级所需字段（指定quote bind）
"""
import sys
import os
from sqlalchemy import text, inspect

sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app, db
from app.models.quote import Quote, QuoteTemplate

def run_migration():
    app = create_app()
    with app.app_context():
        # 获取quote bind的engine（传入app参数）
        quote_engine = db.get_engine(app, bind='quote')
        inspector = inspect(quote_engine)
        
        try:
            columns = [col['name'] for col in inspector.get_columns('quote')]
        except Exception as e:
            print(f"获取字段失败: {e}")
            return
        
        print(f"当前quote表字段: {columns}")
        
        # 定义要添加的新字段（逐个添加，SQLite不支持多列）
        new_fields = []
        if 'project_name' not in columns:
            new_fields.append(("project_name", "VARCHAR(200)"))
        if 'project_address' not in columns:
            new_fields.append(("project_address", "VARCHAR(500)"))
        if 'house_type' not in columns:
            new_fields.append(("house_type", "VARCHAR(50)"))
        if 'related_case_id' not in columns:
            new_fields.append(("related_case_id", "INTEGER"))
        if 'contract_no' not in columns:
            new_fields.append(("contract_no", "VARCHAR(50)"))
        if 'cover_template_id' not in columns:
            new_fields.append(("cover_template_id", "INTEGER"))
        
        if new_fields:
            with quote_engine.connect() as conn:
                for col_name, col_type in new_fields:
                    sql = f"ALTER TABLE quote ADD COLUMN {col_name} {col_type}"
                    print(f"执行SQL: {sql}")
                    try:
                        conn.execute(text(sql))
                        conn.commit()
                        print(f"  添加字段 {col_name} 成功")
                    except Exception as e:
                        print(f"  添加字段 {col_name} 失败: {e}")
            print("✅ 迁移完成")
        else:
            print("✅ 所有字段已存在，无需迁移")
        
        # 验证新字段
        columns_after = [col['name'] for col in inspector.get_columns('quote')]
        print(f"迁移后字段: {columns_after}")

if __name__ == '__main__':
    run_migration()
