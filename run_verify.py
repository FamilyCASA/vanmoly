import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

DB_PATH = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 统计有主图的西映物料
cursor.execute("""
    SELECT COUNT(*) as cnt FROM material_sku 
    WHERE sku_code LIKE 'XY-%' AND main_image IS NOT NULL
""")
with_image = cursor.fetchone()['cnt']

cursor.execute("""
    SELECT COUNT(*) as cnt FROM material_sku 
    WHERE sku_code LIKE 'XY-%'
""")
total = cursor.fetchone()['cnt']

print(f'西映物料总数: {total}')
print(f'有主图的物料: {with_image}')
print(f'覆盖率: {with_image/total*100:.1f}%')

# 显示前5条带图片的物料
cursor.execute("""
    SELECT sku_code, name, main_image 
    FROM material_sku 
    WHERE sku_code LIKE 'XY-%' AND main_image IS NOT NULL
    LIMIT 5
""")
rows = cursor.fetchall()
print('\n前5条带图片的物料:')
for row in rows:
    print(f'  {row["sku_code"]}')
    print(f'    名称: {row["name"]}')
    print(f'    图片: {row["main_image"]}')

conn.close()
