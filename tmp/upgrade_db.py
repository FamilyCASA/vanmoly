#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
V3.2 数据库升级脚本
执行Phase 1数据库升级
"""
import sqlite3
import shutil
import os
import sys
from datetime import datetime

# 强制UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 路径配置
# tmp目录在项目根目录，数据库在backend/instance/
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'backend', 'instance', 'vanmoly_v3.db')
BACKUP_PATH = os.path.join(PROJECT_DIR, 'backend', 'instance', f'vanmoly_v3_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
SQL_PATH = os.path.join(PROJECT_DIR, 'tmp', 'v3.2_upgrade_phase1.sql')

def main():
    print("=" * 60)
    print("VANMOLY-SYS V3.2 数据库升级")
    print("=" * 60)
    
    # 1. 检查数据库
    if not os.path.exists(DB_PATH):
        print(f"[X] 数据库不存在: {DB_PATH}")
        return False
    
    print(f"[OK] 数据库路径: {DB_PATH}")
    print(f"   大小: {os.path.getsize(DB_PATH):,} bytes")
    
    # 2. 备份数据库
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"[OK] 已备份到: {BACKUP_PATH}")
    
    # 3. 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("[OK] 数据库连接成功")
    
    # 4. 检查表是否存在
    print("\n检查现有表...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    print(f"   现有表: {len(existing_tables)} 个")
    
    # 5. 创建新表
    print("\n创建新表...")
    
    new_tables = {
        'case_space_config': """
            CREATE TABLE IF NOT EXISTS case_space_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(32) DEFAULT '0',
                case_id INTEGER NOT NULL,
                quote_id INTEGER,
                space_type VARCHAR(50) NOT NULL,
                space_name VARCHAR(100),
                space_area DECIMAL(10,2),
                version_level VARCHAR(20) NOT NULL,
                version_code VARCHAR(20),
                config_name VARCHAR(200),
                config_desc TEXT,
                materials TEXT,
                material_count INTEGER DEFAULT 0,
                material_cost DECIMAL(12,2) DEFAULT 0,
                labor_cost DECIMAL(12,2) DEFAULT 0,
                design_cost DECIMAL(12,2) DEFAULT 0,
                manage_cost DECIMAL(12,2) DEFAULT 0,
                total_price DECIMAL(12,2) DEFAULT 0,
                is_template INTEGER DEFAULT 1,
                template_tags TEXT,
                exclusive_rules TEXT,
                status VARCHAR(20) DEFAULT 'active',
                created_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES case_study(id),
                FOREIGN KEY (quote_id) REFERENCES quote(id)
            )
        """,
        'case_space_config_item': """
            CREATE TABLE IF NOT EXISTS case_space_config_item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_id INTEGER NOT NULL,
                sku_id INTEGER NOT NULL,
                sku_code VARCHAR(50),
                sku_name VARCHAR(200),
                brand VARCHAR(100),
                specification VARCHAR(200),
                category VARCHAR(50),
                quantity DECIMAL(10,2) DEFAULT 1,
                unit VARCHAR(20),
                unit_price DECIMAL(12,2),
                total_price DECIMAL(12,2),
                is_exclusive INTEGER DEFAULT 0,
                exclusive_group VARCHAR(50),
                is_optional INTEGER DEFAULT 0,
                is_default INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                FOREIGN KEY (config_id) REFERENCES case_space_config(id),
                FOREIGN KEY (sku_id) REFERENCES material_sku(id)
            )
        """,
        'quote_space_instance': """
            CREATE TABLE IF NOT EXISTS quote_space_instance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(32) DEFAULT '0',
                quote_id INTEGER NOT NULL,
                template_config_id INTEGER,
                space_type VARCHAR(50),
                space_name VARCHAR(100),
                space_area DECIMAL(10,2),
                version_level VARCHAR(20),
                original_price DECIMAL(12,2),
                adjusted_price DECIMAL(12,2),
                adjustment_reason TEXT,
                adjustments TEXT,
                is_selected INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quote_id) REFERENCES quote(id),
                FOREIGN KEY (template_config_id) REFERENCES case_space_config(id)
            )
        """,
        'material_exclusive_rule': """
            CREATE TABLE IF NOT EXISTS material_exclusive_rule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id VARCHAR(32) DEFAULT '0',
                rule_name VARCHAR(100),
                rule_group VARCHAR(50),
                sku_id INTEGER,
                exclusive_sku_ids TEXT,
                description TEXT,
                is_enabled INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
    }
    
    created_count = 0
    for table_name, create_sql in new_tables.items():
        if table_name not in existing_tables:
            try:
                cursor.execute(create_sql)
                print(f"   [OK] 创建表: {table_name}")
                created_count += 1
            except Exception as e:
                print(f"   [X] 创建表 {table_name} 失败: {e}")
        else:
            print(f"   [--] 表已存在: {table_name}")
    
    # 6. 创建索引
    print("\n创建索引...")
    indexes = [
        ("idx_case_space_config_case", "case_space_config(case_id)"),
        ("idx_case_space_config_space", "case_space_config(space_type)"),
        ("idx_case_space_config_version", "case_space_config(version_level)"),
        ("idx_config_item_config", "case_space_config_item(config_id)"),
        ("idx_config_item_sku", "case_space_config_item(sku_id)"),
        ("idx_quote_space_quote", "quote_space_instance(quote_id)"),
    ]
    
    for idx_name, idx_sql in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_sql}")
            print(f"   [OK] 索引: {idx_name}")
        except Exception as e:
            print(f"   [!] 索引 {idx_name}: {e}")
    
    # 7. 插入测试数据（示例）
    print("\n插入测试数据...")
    
    # 检查是否有案例数据
    cursor.execute("SELECT id, title, style, total_price FROM case_study LIMIT 3")
    cases = cursor.fetchall()
    
    if cases:
        for case in cases:
            case_id, title, style, total_price = case
            
            # 为每个案例创建三个版本的空间配置
            space_types = ['客厅', '主卧', '餐厅']
            versions = [
                ('舒适', 'C', 0.15),
                ('豪华', 'H', 0.22),
                ('顶配', 'T', 0.35)
            ]
            
            for space_type in space_types:
                for version_name, version_code, price_ratio in versions:
                    # 计算价格
                    base_price = float(total_price or 100000)
                    space_price = base_price * price_ratio
                    
                    # 检查是否已存在
                    cursor.execute("""
                        SELECT id FROM case_space_config 
                        WHERE case_id = ? AND space_type = ? AND version_level = ?
                    """, (case_id, space_type, version_name))
                    
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO case_space_config 
                            (case_id, space_type, space_name, version_level, version_code, 
                             config_name, total_price, is_template, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'active')
                        """, (
                            case_id, space_type, space_type, version_name, version_code,
                            f"{style or '现代'}-{space_type}-{version_name}版",
                            space_price
                        ))
        
        print(f"   [OK] 已为 {len(cases)} 个案例创建示例配置")
    
    # 8. 提交并验证
    conn.commit()
    
    # 验证
    print("\n验证升级结果...")
    cursor.execute("SELECT COUNT(*) FROM case_space_config")
    config_count = cursor.fetchone()[0]
    print(f"   [OK] case_space_config: {config_count} 条记录")
    
    cursor.execute("SELECT COUNT(*) FROM case_space_config_item")
    item_count = cursor.fetchone()[0]
    print(f"   [OK] case_space_config_item: {item_count} 条记录")
    
    cursor.execute("SELECT COUNT(*) FROM quote_space_instance")
    instance_count = cursor.fetchone()[0]
    print(f"   [OK] quote_space_instance: {instance_count} 条记录")
    
    # 9. 查看示例数据
    print("\n示例配置数据:")
    cursor.execute("""
        SELECT case_id, space_type, version_level, config_name, total_price 
        FROM case_space_config 
        ORDER BY case_id, space_type, version_level
        LIMIT 9
    """)
    
    for row in cursor.fetchall():
        print(f"   案例ID:{row[0]:3d} | {row[1]:6s} | {row[2]:4s} | ¥{row[4]:,.0f} | {row[3]}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("[OK] Phase 1 数据库升级完成！")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    main()
