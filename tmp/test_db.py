#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试数据库升级结果"""
import sqlite3
import os

db_path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== 数据库表检查 ===')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%space%'")
tables = cursor.fetchall()
print('空间相关表:', tables)

print('\n=== case_space_config 表结构 ===')
cursor.execute('PRAGMA table_info(case_space_config)')
for col in cursor.fetchall():
    print(f'  {col[1]:20s} {col[2]:15s} {col[3]}')

print('\n=== 示例数据 ===')
cursor.execute('SELECT id, case_id, space_type, version_level, total_price, config_name FROM case_space_config LIMIT 5')
for row in cursor.fetchall():
    print(f'  ID:{row[0]:3d} 案例:{row[1]:3d} {row[2]:8s} {row[3]:6s} {row[4]:>10,.0f} {row[5]}')

conn.close()
