import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

DB_PATH = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("更新西映物料销售价 (成本价 × 3)")
print("=" * 60)

# 查看当前价格情况
cursor.execute("""
    SELECT 
        COUNT(*) as cnt,
        ROUND(AVG(cost_price), 2) as avg_cost,
        ROUND(AVG(sale_price), 2) as avg_sale
    FROM material_sku 
    WHERE sku_code LIKE 'XY-%'
""")
old = cursor.fetchone()
print(f"\n【更新前】")
print(f"  物料数: {old['cnt']}")
print(f"  平均成本价: ¥{old['avg_cost']}")
print(f"  平均销售价: ¥{old['avg_sale']}")
print(f"  当前倍数: {old['avg_sale']/old['avg_cost']:.1f}x")

# 更新销售价为成本价的3倍
cursor.execute("""
    UPDATE material_sku 
    SET sale_price = ROUND(cost_price * 3, 2)
    WHERE sku_code LIKE 'XY-%'
""")
updated = cursor.rowcount
conn.commit()

# 查看更新后价格情况
cursor.execute("""
    SELECT 
        COUNT(*) as cnt,
        ROUND(AVG(cost_price), 2) as avg_cost,
        ROUND(AVG(sale_price), 2) as avg_sale,
        ROUND(MIN(sale_price), 2) as min_sale,
        ROUND(MAX(sale_price), 2) as max_sale
    FROM material_sku 
    WHERE sku_code LIKE 'XY-%'
""")
new = cursor.fetchone()
print(f"\n【更新后】")
print(f"  更新物料数: {updated}")
print(f"  平均成本价: ¥{new['avg_cost']}")
print(f"  平均销售价: ¥{new['avg_sale']}")
print(f"  销售价区间: ¥{new['min_sale']} - ¥{new['max_sale']}")
print(f"  新倍数: {new['avg_sale']/new['avg_cost']:.1f}x")

# 显示部分示例
cursor.execute("""
    SELECT sku_code, name, cost_price, sale_price
    FROM material_sku 
    WHERE sku_code LIKE 'XY-%'
    ORDER BY id
    LIMIT 8
""")
rows = cursor.fetchall()
print(f"\n【价格示例】")
for row in rows:
    multiple = row['sale_price'] / row['cost_price'] if row['cost_price'] else 0
    print(f"  {row['sku_code'][:20]:<20} 成本¥{row['cost_price']:>8} → 销售¥{row['sale_price']:>8} ({multiple:.0f}x)")

conn.close()

print("\n" + "=" * 60)
print("价格更新完成！所有销售价已调整为成本价的3倍")
print("=" * 60)
