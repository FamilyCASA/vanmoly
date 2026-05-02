import sqlite3

DB_PATH = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 统计西映品牌物料总数
cursor.execute("SELECT COUNT(*) FROM material_sku WHERE sku_code LIKE 'XY-%'")
count = cursor.fetchone()[0]
print(f'西映品牌物料总数: {count}')

# 按分类统计
cursor.execute("""
    SELECT c.name, COUNT(s.id) 
    FROM material_sku s 
    JOIN material_category c ON s.category_id = c.id 
    WHERE s.sku_code LIKE 'XY-%'
    GROUP BY c.name
""")
categories = cursor.fetchall()
print('\n按分类统计:')
for cat in categories:
    print(f'  {cat[0]}: {cat[1]} 条')

# 显示前5条数据
cursor.execute("""
    SELECT sku_code, name, brand, cost_price, sale_price 
    FROM material_sku 
    WHERE sku_code LIKE 'XY-%' 
    LIMIT 5
""")
rows = cursor.fetchall()
print('\n前5条数据示例:')
for row in rows:
    print(f'  {row[0]} | {row[1]} | 成本:{row[3]} | 销售价:{row[4]}')

conn.close()
print('\n验证完成!')
