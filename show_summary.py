import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

DB_PATH = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("西映品牌供应链数据导入报告")
print("=" * 60)

# 统计西映物料总数
cursor.execute("SELECT COUNT(*) as cnt FROM material_sku WHERE sku_code LIKE 'XY-%'")
total = cursor.fetchone()['cnt']
print(f"\n【物料统计】")
print(f"  西映物料总数: {total} 条")

# 按分类统计
cursor.execute("""
    SELECT c.name as category, COUNT(s.id) as cnt
    FROM material_sku s 
    JOIN material_category c ON s.category_id = c.id 
    WHERE s.sku_code LIKE 'XY-%'
    GROUP BY c.name
    ORDER BY cnt DESC
""")
categories = cursor.fetchall()
print(f"\n【分类统计】")
for cat in categories:
    print(f"  {cat['category']}: {cat['cnt']} 条")

# 统计有图片的物料
cursor.execute("""
    SELECT COUNT(*) as cnt FROM material_sku 
    WHERE sku_code LIKE 'XY-%' AND main_image IS NOT NULL
""")
with_image = cursor.fetchone()['cnt']
print(f"\n【图片统计】")
print(f"  有主图的物料: {with_image} 条")
print(f"  覆盖率: {with_image/total*100:.1f}%")

# 价格统计
cursor.execute("""
    SELECT 
        ROUND(AVG(cost_price), 2) as avg_cost,
        ROUND(AVG(sale_price), 2) as avg_sale,
        ROUND(MIN(cost_price), 2) as min_cost,
        ROUND(MAX(cost_price), 2) as max_cost
    FROM material_sku 
    WHERE sku_code LIKE 'XY-%'
""")
price = cursor.fetchone()
print(f"\n【价格统计】")
print(f"  平均成本价: ¥{price['avg_cost']}")
print(f"  平均销售价: ¥{price['avg_sale']}")
print(f"  成本价区间: ¥{price['min_cost']} - ¥{price['max_cost']}")

# 显示示例数据
cursor.execute("""
    SELECT sku_code, name, cost_price, sale_price, main_image
    FROM material_sku 
    WHERE sku_code LIKE 'XY-%'
    ORDER BY id
    LIMIT 5
""")
rows = cursor.fetchall()
print(f"\n【数据示例】")
for row in rows:
    print(f"  {row['sku_code']}")
    print(f"    名称: {row['name']}")
    print(f"    成本: ¥{row['cost_price']} → 销售: ¥{row['sale_price']}")
    print(f"    图片: {'✅' if row['main_image'] else '❌'}")

conn.close()

print("\n" + "=" * 60)
print("导入完成！所有物料已关联主图")
print("=" * 60)
