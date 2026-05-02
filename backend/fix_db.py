import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'vanmoly_v3.db')

print(f'数据库路径: {DB_PATH}')

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 检查 customer 表的列
cursor.execute("PRAGMA table_info(customer)")
columns = cursor.fetchall()
print('\n当前 customer 表列:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

# 检查是否有 last_login_at 列
has_last_login = any(col[1] == 'last_login_at' for col in columns)
print(f'\n是否有 last_login_at 列: {has_last_login}')

if not has_last_login:
    print('添加 last_login_at 列...')
    cursor.execute('ALTER TABLE customer ADD COLUMN last_login_at DATETIME')
    conn.commit()
    print('列添加成功！')

# 检查其他可能缺失的列
expected_columns = ['password_hash', 'last_login_at']
for col_name in expected_columns:
    has_col = any(col[1] == col_name for col in columns)
    if not has_col:
        print(f'添加缺失的列: {col_name}')
        if col_name == 'password_hash':
            cursor.execute('ALTER TABLE customer ADD COLUMN password_hash VARCHAR(128)')
        conn.commit()
        print(f'列 {col_name} 添加成功！')

conn.close()
print('\n数据库修复完成！')
