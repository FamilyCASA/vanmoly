#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""添加 is_top 列到案例表"""
import sqlite3

DB_PATH = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 检查表结构
print('=== 检查案例表结构 ===')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%case%'")
case_tables = cursor.fetchall()
print(f'案例相关表: {[t[0] for t in case_tables]}')

# 检查 case_study 表（根据模型文件应该是 case_study 单数）
for table_name in ['case_study', 'case_studies', 'cases']:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        print(f'\n表 {table_name} 有 {count} 条记录')
        
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = [col[1] for col in cursor.fetchall()]
        print(f'列: {columns}')
        
        if 'is_top' not in columns:
            print(f'添加 is_top 列到 {table_name}...')
            cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN is_top BOOLEAN DEFAULT 0')
            conn.commit()
            print('✅ is_top 列已添加')
        else:
            print('✅ is_top 列已存在')
        break
    except sqlite3.OperationalError as e:
        continue

conn.close()
