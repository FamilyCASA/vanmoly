"""
V3.3 幻灯片演示+9阶段+物料配置 升级 - 数据库迁移脚本
执行方式: python migrate_v33_slide_upgrade.py
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

app = create_app()


def table_exists(table_name):
    """检查表是否存在"""
    result = db.session.execute(text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=:name"
    ), {'name': table_name})
    return result.fetchone() is not None


def column_exists(table_name, column_name):
    """检查列是否存在"""
    result = db.session.execute(text(f"PRAGMA table_info({table_name})"))
    columns = [row[1] for row in result]
    return column_name in columns


def migrate():
    with app.app_context():
        print("=" * 60)
        print("V3.3 Slide + 9-Phase + Material Config - DB Migration")
        print("=" * 60)

        # 1. 给case_phases表添加阶段7-9字段
        print("\n[1/4] Add Phase 7-9 columns to case_phases...")

        phase7_cols = [
            ('material_gallery', 'TEXT'),
            ('material_specs', 'TEXT'),
        ]
        phase8_cols = [
            ('product_gallery', 'TEXT'),
            ('product_list', 'TEXT'),
        ]
        phase9_cols = [
            ('process_gallery', 'TEXT'),
            ('process_desc', 'TEXT'),
        ]

        all_new_cols = phase7_cols + phase8_cols + phase9_cols

        for col_name, col_type in all_new_cols:
            if not column_exists('case_phases', col_name):
                print(f"  [ADD] Adding {col_name} ({col_type})...")
                db.session.execute(text(
                    f"ALTER TABLE case_phases ADD COLUMN {col_name} {col_type}"
                ))
                db.session.commit()
                print(f"  [OK] {col_name} added")
            else:
                print(f"  [OK] {col_name} already exists")

        # 2. 创建case_space_materials表
        print("\n[2/4] Create case_space_materials table...")
        if not table_exists('case_space_materials'):
            db.session.execute(text("""
                CREATE TABLE case_space_materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    space_id INTEGER NOT NULL REFERENCES case_space_renderings(id),
                    case_id INTEGER NOT NULL REFERENCES case_study(id),
                    space_name VARCHAR(100),
                    room_name VARCHAR(50),
                    sku_id INTEGER,
                    sku_code VARCHAR(50),
                    material_name VARCHAR(200),
                    material_image VARCHAR(500),
                    category_level1 VARCHAR(50),
                    category_level2 VARCHAR(50),
                    category_level3 VARCHAR(50),
                    brand VARCHAR(100),
                    spec VARCHAR(200),
                    unit VARCHAR(20),
                    quantity DECIMAL(10,2) DEFAULT 1,
                    unit_price DECIMAL(10,2) DEFAULT 0,
                    total_price DECIMAL(12,2) DEFAULT 0,
                    sort_order INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            print("  [OK] case_space_materials table created")
        else:
            print("  [OK] case_space_materials table already exists")

        # 3. 创建case_slide_configs表
        print("\n[3/4] Create case_slide_configs table...")
        if not table_exists('case_slide_configs'):
            db.session.execute(text("""
                CREATE TABLE case_slide_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER NOT NULL UNIQUE REFERENCES case_study(id),
                    template_style VARCHAR(50) DEFAULT 'modern',
                    primary_color VARCHAR(7) DEFAULT '#8B4513',
                    cover_title VARCHAR(200),
                    cover_subtitle VARCHAR(200),
                    cover_bg_image VARCHAR(500),
                    about_title VARCHAR(200) DEFAULT '关于我们',
                    about_content TEXT,
                    about_image VARCHAR(500),
                    show_about BOOLEAN DEFAULT 1,
                    show_team BOOLEAN DEFAULT 1,
                    show_toc BOOLEAN DEFAULT 1,
                    show_material BOOLEAN DEFAULT 1,
                    show_product BOOLEAN DEFAULT 1,
                    show_process BOOLEAN DEFAULT 1,
                    show_summary BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            print("  [OK] case_slide_configs table created")
        else:
            print("  [OK] case_slide_configs table already exists")

        # 4. 验证
        print("\n[4/4] Verification...")
        # Check case_phases columns
        for col_name, _ in all_new_cols:
            assert column_exists('case_phases', col_name), f"Missing column: {col_name}"
        print("  [OK] case_phases: all Phase 7-9 columns present")

        assert table_exists('case_space_materials'), "Missing table: case_space_materials"
        print("  [OK] case_space_materials table exists")

        assert table_exists('case_slide_configs'), "Missing table: case_slide_configs"
        print("  [OK] case_slide_configs table exists")

        print("\n" + "=" * 60)
        print("✅ V3.3 Migration completed successfully!")
        print("=" * 60)


if __name__ == '__main__':
    migrate()
