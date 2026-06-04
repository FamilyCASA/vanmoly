"""
V3.2 视觉素材6阶段升级 - 数据库迁移脚本
执行方式: python migrate_v32_phases.py
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("=" * 60)
        print("V3.2 Visual Material 6-Phase Upgrade - DB Migration")
        print("=" * 60)
        
        # 1. 给case_study表添加quote_id字段
        print("\n[1/4] Check case_study.quote_id field...")
        try:
            db.session.execute(text("SELECT quote_id FROM case_study LIMIT 1"))
            print("  [OK] quote_id field exists")
        except Exception:
            print("  [ADD] Adding quote_id field...")
            db.session.execute(text("""
                ALTER TABLE case_study ADD COLUMN quote_id INTEGER
            """))
            db.session.commit()
            print("  [OK] quote_id field added")
        
        # 2. 创建case_phases表
        print("\n[2/4] Check case_phases table...")
        try:
            db.session.execute(text("SELECT id FROM case_phases LIMIT 1"))
            print("  [OK] case_phases table exists")
        except Exception:
            print("  [ADD] Creating case_phases table...")
            db.session.execute(text("""
                CREATE TABLE case_phases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER NOT NULL,
                    phase_number INTEGER NOT NULL,
                    phase_name VARCHAR(50),
                    layout_images TEXT,
                    layout_analysis TEXT,
                    mood_images TEXT,
                    mood_text TEXT,
                    plan_image VARCHAR(500),
                    plan_text TEXT,
                    birdview_images TEXT,
                    showcase_images TEXT,
                    showcase_title1 VARCHAR(200),
                    showcase_title2 VARCHAR(200),
                    showcase_text_cn TEXT,
                    showcase_text_en TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES case_study(id) ON DELETE CASCADE
                )
            """))
            db.session.commit()
            print("  [OK] case_phases table created")
        
        # 3. 创建case_space_renderings表
        print("\n[3/4] Check case_space_renderings table...")
        try:
            db.session.execute(text("SELECT id FROM case_space_renderings LIMIT 1"))
            print("  [OK] case_space_renderings table exists")
        except Exception:
            print("  [ADD] Creating case_space_renderings table...")
            db.session.execute(text("""
                CREATE TABLE case_space_renderings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER NOT NULL,
                    space_name VARCHAR(100) NOT NULL,
                    sort_order INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES case_study(id) ON DELETE CASCADE
                )
            """))
            db.session.commit()
            print("  [OK] case_space_renderings table created")
        
        # 4. 创建case_rendering_items表
        print("\n[4/4] Check case_rendering_items table...")
        try:
            db.session.execute(text("SELECT id FROM case_rendering_items LIMIT 1"))
            print("  [OK] case_rendering_items table exists")
        except Exception:
            print("  [ADD] Creating case_rendering_items table...")
            db.session.execute(text("""
                CREATE TABLE case_rendering_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    space_id INTEGER NOT NULL,
                    image_url VARCHAR(500) NOT NULL,
                    title VARCHAR(200),
                    description TEXT,
                    sort_order INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (space_id) REFERENCES case_space_renderings(id) ON DELETE CASCADE
                )
            """))
            db.session.commit()
            print("  [OK] case_rendering_items table created")
        
        print("\n" + "=" * 60)
        print("Migration Complete!")
        print("=" * 60)
        
        # 验证
        print("\nVerify new tables:")
        for table in ['case_phases', 'case_space_renderings', 'case_rendering_items']:
            result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  {table}: {count} records")


if __name__ == '__main__':
    migrate()
