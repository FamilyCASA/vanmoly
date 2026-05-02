#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import os

os.chdir(r'D:\desktop\VANMOLY-SYS-V3.0\backend')
conn = sqlite3.connect('vanmoly_v3.db')
cursor = conn.cursor()

# 列出所有表
print('=== 数据库中的表 ===')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for t in tables:
    print(f'  - {t[0]}')

# 找到案例相关的表
case_tables = [t[0] for t in tables if 'case' in t[0].lower()]
print(f'\n案例相关表: {case_tables}')

for table in case_tables:
    print(f'\n=== {table} 表结构 ===')
    cursor.execute(f'PRAGMA table_info({table})')
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]}: {col[2]}')

conn.close()
