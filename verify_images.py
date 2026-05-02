import sqlite3

DB_PATH = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 统计有主图的西映物料
cursor.execute("""
    SELECT COUNT(*) FROM material_sku 
    WHERE sku_code LIKE 'XY-%' AND main_image IS NOT NULL
""")
with_image = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) FROM material_sku 
    WHERE sku_code LIKE 'XY-%'
""")
total = cursor.fetchone()[0]

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
    print(f'  {row[0]}')
    print(f'    名称: {row[1]}')
    print(f'    图片: {row[2]}')

conn.close()
