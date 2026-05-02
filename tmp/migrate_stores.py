# -*- coding: utf-8 -*-
"""数据库迁移：添加Store表新字段"""

import sqlite3
import os

DB_PATH = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'

def migrate_stores_table():
    """迁移stores表"""
    
    # 备份数据库
    import shutil
    from datetime import datetime
    backup_path = DB_PATH.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    shutil.copy2(DB_PATH, backup_path)
    print(f'[备份] {backup_path}')
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取当前表结构
    cursor.execute("PRAGMA table_info(stores)")
    existing_columns = {row[1]: row[2] for row in cursor.fetchall()}
    print(f'\n现有字段: {list(existing_columns.keys())}')
    
    # 需要添加的新字段
    new_columns = [
        ('tenant_id', 'VARCHAR(32)'),
        ('db_path', 'VARCHAR(255)'),
        ('db_status', 'VARCHAR(20) DEFAULT "pending"'),
        ('province', 'VARCHAR(50)'),
        ('city', 'VARCHAR(50)'),
        ('district', 'VARCHAR(50)'),
        ('opening_date', 'DATE'),
        ('business_hours', 'VARCHAR(100)'),
        ('description', 'TEXT'),
        ('updated_at', 'DATETIME')
    ]
    
    # 添加缺失字段
    added = []
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                sql = f'ALTER TABLE stores ADD COLUMN {col_name} {col_type}'
                cursor.execute(sql)
                added.append(col_name)
                print(f'[添加] {col_name} {col_type}')
            except Exception as e:
                print(f'[错误] {col_name}: {e}')
    
    # 提交更改
    conn.commit()
    
    # 更新现有记录，为tenant_id生成值
    if 'tenant_id' in added:
        cursor.execute("SELECT id, code FROM stores WHERE tenant_id IS NULL")
        stores = cursor.fetchall()
        for store_id, code in stores:
            tenant_id = f"tenant_{code.lower()}" if code else f"tenant_{store_id}"
            cursor.execute("UPDATE stores SET tenant_id = ?, db_status = 'pending' WHERE id = ?", 
                         (tenant_id, store_id))
        conn.commit()
        print(f'\n[更新] 为 {len(stores)} 条记录生成 tenant_id')
    
    # 验证迁移结果
    cursor.execute("PRAGMA table_info(stores)")
    final_columns = [row[1] for row in cursor.fetchall()]
    print(f'\n迁移后字段: {final_columns}')
    
    conn.close()
    print('\n迁移完成！')

if __name__ == '__main__':
    migrate_stores_table()
