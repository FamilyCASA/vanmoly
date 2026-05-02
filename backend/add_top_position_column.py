#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""添加 top_position 列到案例表"""
import sqlite3

DB_PATH = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # 检查 top_position 列是否已存在
    cursor.execute('PRAGMA table_info(case_study)')
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'top_position' not in columns:
        print('Adding top_position column...')
        cursor.execute('ALTER TABLE case_study ADD COLUMN top_position INTEGER')
        conn.commit()
        print('top_position column added successfully')
    else:
        print('top_position column already exists')
        
except Exception as e:
    print(f'Error: {e}')
finally:
    conn.close()
