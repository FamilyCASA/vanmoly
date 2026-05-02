"""
线索管理 V2.0 数据库迁移脚本
从旧版 Lead 模型迁移到新版
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text


def migrate_lead_v2():
    """执行线索表升级迁移"""
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("线索管理 V2.0 数据库迁移")
        print("=" * 50)
        
        # 检查是否需要迁移
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('lead')]
        
        if 'conversion_level' in columns:
            print("数据库已经是最新版本，无需迁移")
            return
        
        print("\n[1/5] 备份旧线索表...")
        try:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS lead_backup AS 
                SELECT * FROM lead
            """))
            print("      备份完成: lead_backup")
        except Exception as e:
            print(f"      备份失败: {e}")
        
        print("\n[2/5] 添加新字段到 lead 表...")
        new_columns = [
            ("wechat", "VARCHAR(50)"),
            ("gender", "VARCHAR(10)"),
            ("source_detail", "VARCHAR(100)"),
            ("building_name", "VARCHAR(100)"),
            ("building_address", "VARCHAR(200)"),
            ("floor", "VARCHAR(20)"),
            ("delivery_date", "DATE"),
            ("decoration_status", "VARCHAR(50)"),
            ("decoration_type", "VARCHAR(50)"),
            ("style_preference", "VARCHAR(100)"),
            ("timeline", "VARCHAR(50)"),
            ("detailed_needs", "TEXT"),
            ("family_structure", "VARCHAR(200)"),
            ("living_habits", "VARCHAR(500)"),
            ("hobbies", "VARCHAR(200)"),
            ("special_requirements", "VARCHAR(500)"),
            ("focus_points", "VARCHAR(500)"),
            ("tags", "JSON"),
            ("intention_level", "VARCHAR(20) DEFAULT '中'"),
            ("conversion_level", "VARCHAR(20) DEFAULT '线索'"),
            ("assigned_at", "DATETIME"),
            ("assigned_by", "INTEGER"),
            ("next_follow_at", "DATETIME"),
            ("is_overdue", "BOOLEAN DEFAULT 0"),
            ("overdue_days", "INTEGER DEFAULT 0"),
            ("is_visited", "BOOLEAN DEFAULT 0"),
            ("visited_at", "DATETIME"),
            ("is_measured", "BOOLEAN DEFAULT 0"),
            ("measured_at", "DATETIME"),
            ("has_scheme", "BOOLEAN DEFAULT 0"),
            ("scheme_at", "DATETIME"),
            ("deposit_amount", "NUMERIC(12,2)"),
            ("deposit_at", "DATETIME"),
            ("contract_type", "VARCHAR(50)"),
            ("contract_amount", "NUMERIC(12,2)"),
            ("contract_at", "DATETIME"),
            ("deal_at", "DATETIME"),
            ("is_in_sea", "BOOLEAN DEFAULT 0"),
            ("sea_at", "DATETIME"),
            ("sea_reason", "VARCHAR(100)"),
            ("sea_retrieved_by", "INTEGER"),
            ("sea_retrieved_at", "DATETIME"),
            ("total_points", "INTEGER DEFAULT 0"),
            ("is_invalid", "BOOLEAN DEFAULT 0"),
            ("invalid_reason", "VARCHAR(200)"),
            ("created_by", "INTEGER"),
        ]
        
        for col_name, col_type in new_columns:
            try:
                db.session.execute(text(f"""
                    ALTER TABLE lead ADD COLUMN {col_name} {col_type}
                """))
                print(f"      添加字段: {col_name}")
            except Exception as e:
                print(f"      字段 {col_name} 已存在或添加失败: {e}")
        
        print("\n[3/5] 更新旧数据...")
        
        # 更新状态字段
        status_map = {
            '新线索': '待分配',
            '已联系': '跟进中',
            '已到店': '已到店',
            '已成交': '已签约',
            '无效': '无效'
        }
        
        for old_status, new_status in status_map.items():
            try:
                result = db.session.execute(text("""
                    UPDATE lead SET status = :new_status WHERE status = :old_status
                """), {'new_status': new_status, 'old_status': old_status})
                print(f"      更新状态: {old_status} -> {new_status} ({result.rowcount} 条)")
            except Exception as e:
                print(f"      更新状态失败: {e}")
        
        # 根据现有数据设置意向等级
        try:
            db.session.execute(text("""
                UPDATE lead SET intention_level = '中' WHERE intention_level IS NULL
            """))
            print("      设置默认意向等级")
        except Exception as e:
            print(f"      设置意向等级失败: {e}")
        
        # 根据现有数据设置转化等级
        try:
            db.session.execute(text("""
                UPDATE lead SET conversion_level = '线索' WHERE conversion_level IS NULL
            """))
            print("      设置默认转化等级")
        except Exception as e:
            print(f"      设置转化等级失败: {e}")
        
        print("\n[4/5] 创建新表...")
        
        # 创建 lead_follow 表（如果存在则跳过）
        try:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS lead_follow (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER NOT NULL,
                    follow_type VARCHAR(20),
                    content TEXT,
                    result VARCHAR(100),
                    next_follow_at DATETIME,
                    is_visited BOOLEAN DEFAULT 0,
                    visited_at DATETIME,
                    attachments JSON,
                    operator_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES lead(id)
                )
            """))
            print("      创建表: lead_follow")
        except Exception as e:
            print(f"      创建 lead_follow 失败: {e}")
        
        # 创建 lead_point 表
        try:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS lead_point (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    point_type VARCHAR(50) NOT NULL,
                    points INTEGER NOT NULL,
                    description VARCHAR(200),
                    related_follow_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES lead(id)
                )
            """))
            print("      创建表: lead_point")
        except Exception as e:
            print(f"      创建 lead_point 失败: {e}")
        
        # 创建 lead_distribution 表
        try:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS lead_distribution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER NOT NULL,
                    from_employee_id INTEGER,
                    to_employee_id INTEGER NOT NULL,
                    distributed_by INTEGER,
                    distribution_type VARCHAR(20),
                    reason VARCHAR(200),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES lead(id)
                )
            """))
            print("      创建表: lead_distribution")
        except Exception as e:
            print(f"      创建 lead_distribution 失败: {e}")
        
        # 创建 lead_channel_stat 表
        try:
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS lead_channel_stat (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_date DATE NOT NULL,
                    channel VARCHAR(50) NOT NULL,
                    lead_count INTEGER DEFAULT 0,
                    valid_count INTEGER DEFAULT 0,
                    follow_count INTEGER DEFAULT 0,
                    visit_count INTEGER DEFAULT 0,
                    deposit_count INTEGER DEFAULT 0,
                    contract_count INTEGER DEFAULT 0,
                    deal_amount NUMERIC(12,2) DEFAULT 0,
                    cost NUMERIC(12,2) DEFAULT 0,
                    tenant_id VARCHAR(20),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("      创建表: lead_channel_stat")
        except Exception as e:
            print(f"      创建 lead_channel_stat 失败: {e}")
        
        print("\n[5/5] 提交事务...")
        db.session.commit()
        
        print("\n" + "=" * 50)
        print("迁移完成！")
        print("=" * 50)
        print("\n请重启后端服务以应用更改")
        

def rollback_migration():
    """回滚迁移（谨慎使用）"""
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("回滚线索管理 V2.0 迁移")
        print("=" * 50)
        
        confirm = input("确定要回滚吗？这将删除所有 V2.0 数据！(yes/no): ")
        if confirm.lower() != 'yes':
            print("取消回滚")
            return
        
        try:
            # 从新表恢复数据到旧表
            db.session.execute(text("""
                INSERT OR REPLACE INTO lead 
                SELECT id, name, phone, source, source_id, source_page,
                       intention, budget, house_type, area, status,
                       assigned_to, follow_count, first_contact_at,
                       last_follow_at, remark, ip_address, user_agent,
                       tenant_id, created_at, updated_at
                FROM lead_backup
            """))
            
            # 删除新表
            db.session.execute(text("DROP TABLE IF EXISTS lead_point"))
            db.session.execute(text("DROP TABLE IF EXISTS lead_distribution"))
            db.session.execute(text("DROP TABLE IF EXISTS lead_channel_stat"))
            
            db.session.commit()
            print("回滚完成")
            
        except Exception as e:
            print(f"回滚失败: {e}")
            db.session.rollback()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='线索管理 V2.0 数据库迁移')
    parser.add_argument('--rollback', action='store_true', help='回滚迁移')
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration()
    else:
        migrate_lead_v2()
