import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

# 直接查数据库
conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cursor = conn.cursor()

# 列出所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('所有表:', [t[0] for t in tables])
conn.close()
