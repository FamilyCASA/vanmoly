import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'vanmoly_v3.db')

print(f'数据库路径: {DB_PATH}')

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 检查 employee 表
cursor.execute("PRAGMA table_info(employee)")
columns = cursor.fetchall()
print('\n当前 employee 表列:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

has_join_date = any(col[1] == 'join_date' for col in columns)
print(f'\n是否有 join_date 列: {has_join_date}')

if not has_join_date:
    print('添加 join_date 列...')
    cursor.execute('ALTER TABLE employee ADD COLUMN join_date DATETIME')
    conn.commit()
    print('列添加成功！')

conn.close()
print('\n数据库修复完成！')
