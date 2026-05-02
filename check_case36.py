# -*- coding: utf-8 -*-
import sqlite3, os

conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cur = conn.cursor()

# 列出所有表
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)

# 检查 case_study 表的所有列
print('\ncase_study columns:')
cur.execute("PRAGMA table_info(case_study)")
for r in cur.fetchall():
    print(f'  {r[1]} ({r[2]})')

# 检查案例36的实际数据
print('\nCase 36 cover_image:')
cur.execute("SELECT id, cover_image FROM case_study WHERE id=36")
row = cur.fetchone()
print(f'  cover_image: {row[1] if row else "NOT FOUND"}')

# 检查 case_media 表
print('\ncase_media columns:')
cur.execute("PRAGMA table_info(case_media)")
for r in cur.fetchall():
    print(f'  {r[1]} ({r[2]})')

# 检查 case_media 数据
print('\ncase_media rows (case_id=36):')
cur.execute("SELECT id, case_id, media_type, url FROM case_media WHERE case_id=36")
for r in cur.fetchall():
    print(f'  {r}')

# 检查 case_files 表
print('\ncase_files columns:')
cur.execute("PRAGMA table_info(case_files)")
for r in cur.fetchall():
    print(f'  {r[1]} ({r[2]})')

# 检查 case_files 数据
print('\ncase_files rows (case_id=36):')
cur.execute("SELECT id, case_id, file_type, file_url, file_name FROM case_files WHERE case_id=36")
for r in cur.fetchall():
    print(f'  {r}')

# 检查文件是否存在
upload_dir = r'D:\desktop\VANMOLY-SYS-V3.0\backend\uploads\cases'
if os.path.exists(upload_dir):
    files = os.listdir(upload_dir)
    print(f'\nFiles in {upload_dir}: {len(files)}')
    for f in sorted(files)[-10:]:
        print(f'  {f}')
else:
    print(f'\n{upload_dir} not found')

conn.close()
