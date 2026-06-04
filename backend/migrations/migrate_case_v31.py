# -*- coding: utf-8 -*-
"""
案例管理 V3.1 数据库迁移脚本
执行: python migrations/migrate_case_v31.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text


def migrate_case_v31():
    """执行案例管理升级迁移"""
    app = create_app()
    
    with app.app_context():
        conn = db.engine.connect()
        
        print("开始案例管理 V3.1 数据库迁移...")
        
        # 1. 扩展 case_study 表
        print("\n[1/8] 扩展 case_study 表...")
        alter_statements = [
            "ALTER TABLE case_study ADD COLUMN case_no VARCHAR(50)",
            "ALTER TABLE case_study ADD COLUMN house_type VARCHAR(50)",
            "ALTER TABLE case_study ADD COLUMN building_id INTEGER",
            "ALTER TABLE case_study ADD COLUMN address VARCHAR(500)",
            "ALTER TABLE case_study ADD COLUMN customer_id INTEGER",
            "ALTER TABLE case_study ADD COLUMN vr_link VARCHAR(500)",
            "ALTER TABLE case_study ADD COLUMN design_concept TEXT",
            "ALTER TABLE case_study ADD COLUMN whole_house_plan TEXT",
            "ALTER TABLE case_study ADD COLUMN customer_requirements TEXT",
            "ALTER TABLE case_study ADD COLUMN design_highlights TEXT",
            "ALTER TABLE case_study ADD COLUMN customer_value TEXT",
            "ALTER TABLE case_study ADD COLUMN total_price DECIMAL(12,2)",
            "ALTER TABLE case_study ADD COLUMN deal_budget DECIMAL(12,2)",
            "ALTER TABLE case_study ADD COLUMN package_type VARCHAR(50)",
            "ALTER TABLE case_study ADD COLUMN price_detail TEXT",
            "ALTER TABLE case_study ADD COLUMN material_list TEXT",
            "ALTER TABLE case_study ADD COLUMN construction_phase VARCHAR(50)",
            "ALTER TABLE case_study ADD COLUMN owner_authorized BOOLEAN DEFAULT 0",
            "ALTER TABLE case_study ADD COLUMN is_public BOOLEAN DEFAULT 1",
            "ALTER TABLE case_study ADD COLUMN publish_time DATETIME",
            "ALTER TABLE case_study ADD COLUMN scheduled_time DATETIME",
            "ALTER TABLE case_study ADD COLUMN sync_xiaohongshu BOOLEAN DEFAULT 0",
            "ALTER TABLE case_study ADD COLUMN sync_mp BOOLEAN DEFAULT 0",
            "ALTER TABLE case_study ADD COLUMN enable_subscription BOOLEAN DEFAULT 1",
            "ALTER TABLE case_study ADD COLUMN enable_notify BOOLEAN DEFAULT 1",
            "ALTER TABLE case_study ADD COLUMN like_count INTEGER DEFAULT 0",
            "ALTER TABLE case_study ADD COLUMN subscription_count INTEGER DEFAULT 0",
            "ALTER TABLE case_study ADD COLUMN lead_count INTEGER DEFAULT 0",
            "ALTER TABLE case_study ADD COLUMN consult_count INTEGER DEFAULT 0",
            "ALTER TABLE case_study ADD COLUMN download_count INTEGER DEFAULT 0",
            "ALTER TABLE case_study ADD COLUMN share_count INTEGER DEFAULT 0",
            "ALTER TABLE case_study ADD COLUMN responsible_id INTEGER",
            "ALTER TABLE case_study ADD COLUMN deleted_at DATETIME",
        ]
        
        for sql in alter_statements:
            try:
                conn.execute(text(sql))
                print("  OK: " + sql[:50])
            except Exception as e:
                if "duplicate column name" in str(e) or "already exists" in str(e):
                    print("  SKIP: " + sql[:40])
                else:
                    print("  ERR: " + str(e))
        
        # 2. 创建 case_timeline 表
        print("\n[2/8] 创建 case_timeline 表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS case_timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                node_time DATETIME NOT NULL,
                title VARCHAR(100),
                content TEXT,
                media_urls TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES case_study(id) ON DELETE CASCADE
            )
        """))
        print("  OK: case_timeline")
        
        # 3. 创建 case_files 表
        print("\n[3/8] 创建 case_files 表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS case_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                file_type VARCHAR(20),
                file_name VARCHAR(200),
                file_url VARCHAR(500),
                has_watermark BOOLEAN DEFAULT 0,
                download_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES case_study(id) ON DELETE CASCADE
            )
        """))
        print("  OK: case_files")
        
        # 4. 创建 case_subscriptions 表
        print("\n[4/8] 创建 case_subscriptions 表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS case_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                user_id INTEGER,
                openid VARCHAR(100),
                subscribe_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                notify_enabled BOOLEAN DEFAULT 1,
                last_notify_time DATETIME,
                FOREIGN KEY (case_id) REFERENCES case_study(id) ON DELETE CASCADE
            )
        """))
        print("  OK: case_subscriptions")
        
        # 5. 创建 case_leads 表
        print("\n[5/8] 创建 case_leads 表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS case_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                name VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                wechat VARCHAR(100),
                source VARCHAR(50),
                message TEXT,
                status VARCHAR(20) DEFAULT 'new',
                contacted_at DATETIME,
                converted_at DATETIME,
                remark TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES case_study(id) ON DELETE CASCADE
            )
        """))
        print("  OK: case_leads")
        
        # 6. 创建 case_templates 表
        print("\n[6/8] 创建 case_templates 表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS case_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name VARCHAR(200),
                package_type VARCHAR(50),
                price_min DECIMAL(12,2),
                price_max DECIMAL(12,2),
                suitable_house_types TEXT,
                base_content TEXT,
                sample_images TEXT,
                created_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("  OK: case_templates")
        
        # 7. 创建 case_notifications 表
        print("\n[7/8] 创建 case_notifications 表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS case_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                notify_type VARCHAR(20),
                content TEXT,
                send_time DATETIME,
                send_status VARCHAR(20) DEFAULT 'pending',
                receiver_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0,
                error_msg TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES case_study(id) ON DELETE CASCADE
            )
        """))
        print("  OK: case_notifications")
        
        # 8. 创建 case_operation_logs 表
        print("\n[8/8] 创建 case_operation_logs 表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS case_operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                operator_id INTEGER,
                operator_name VARCHAR(100),
                operation VARCHAR(50),
                content TEXT,
                ip_address VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES case_study(id) ON DELETE CASCADE
            )
        """))
        print("  OK: case_operation_logs")
        
        # 创建索引
        print("\n[索引] 创建索引...")
        index_statements = [
            "CREATE INDEX IF NOT EXISTS idx_case_study_case_no ON case_study(case_no)",
            "CREATE INDEX IF NOT EXISTS idx_case_study_status ON case_study(status)",
            "CREATE INDEX IF NOT EXISTS idx_case_study_building ON case_study(building_id)",
            "CREATE INDEX IF NOT EXISTS idx_case_study_responsible ON case_study(responsible_id)",
            "CREATE INDEX IF NOT EXISTS idx_case_timeline_case ON case_timeline(case_id)",
            "CREATE INDEX IF NOT EXISTS idx_case_files_case ON case_files(case_id)",
            "CREATE INDEX IF NOT EXISTS idx_case_subscriptions_case ON case_subscriptions(case_id)",
            "CREATE INDEX IF NOT EXISTS idx_case_subscriptions_openid ON case_subscriptions(openid)",
            "CREATE INDEX IF NOT EXISTS idx_case_leads_case ON case_leads(case_id)",
            "CREATE INDEX IF NOT EXISTS idx_case_leads_phone ON case_leads(phone)",
            "CREATE INDEX IF NOT EXISTS idx_case_leads_status ON case_leads(status)",
            "CREATE INDEX IF NOT EXISTS idx_case_notifications_case ON case_notifications(case_id)",
            "CREATE INDEX IF NOT EXISTS idx_case_operation_logs_case ON case_operation_logs(case_id)",
        ]
        
        for sql in index_statements:
            try:
                conn.execute(text(sql))
                print("  OK: " + sql)
            except Exception as e:
                print("  SKIP: " + str(e))
        
        conn.commit()
        print("\n" + "="*50)
        print("案例管理 V3.1 数据库迁移完成!")
        print("="*50)


if __name__ == '__main__':
    migrate_case_v31()
