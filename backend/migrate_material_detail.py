"""
物料表升级 - 增加富文本详情字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("="*60)
        print("Migrating Material SKU Table - Adding detail_content field")
        print("="*60)
        
        # 检查字段是否已存在
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(material_sku)"))
            columns = [row[1] for row in result]
            
            if 'detail_content' in columns:
                print("[INFO] detail_content field already exists, skipping...")
            else:
                # 添加字段
                conn.execute(text("ALTER TABLE material_sku ADD COLUMN detail_content TEXT"))
                conn.commit()
                print("[OK] Added detail_content field to material_sku table")
        
        print("\nMigration complete!")

if __name__ == '__main__':
    migrate()
