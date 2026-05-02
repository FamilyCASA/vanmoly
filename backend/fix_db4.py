import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'vanmoly_v3.db')

print(f'数据库路径: {DB_PATH}')

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 检查 employee 表的所有列
cursor.execute("PRAGMA table_info(employee)")
columns = cursor.fetchall()
print('\n当前 employee 表列:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

# 需要添加的列
needed_columns = ['join_date', 'leave_date', 'resignation_date']
for col_name in needed_columns:
    has_col = any(col[1] == col_name for col in columns)
    print(f'\n是否有 {col_name} 列: {has_col}')
    
    if not has_col:
        print(f'添加 {col_name} 列...')
        cursor.execute(f'ALTER TABLE employee ADD COLUMN {col_name} DATETIME')
        conn.commit()
        print(f'列 {col_name} 添加成功！')

conn.close()
print('\n数据库修复完成！')
