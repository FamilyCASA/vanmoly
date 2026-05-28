import sqlite3
conn = sqlite3.connect('instance/vanmoly_v3.db')
cur = conn.cursor()
# 搜索澜缦集
cur.execute("SELECT id, name, brand, sku_code FROM material_sku WHERE name LIKE '%澜缦集%' OR brand LIKE '%澜缦集%' LIMIT 5")
rows = cur.fetchall()
print(f"=== 澜缦集搜索结果: {len(rows)}条 ===")
for r in rows:
    print(r)

# 也看看回装家具分类下有多少物料
cur.execute("SELECT COUNT(*) FROM material_sku WHERE is_deleted=0 AND category_id IN (SELECT id FROM material_category WHERE parent_id IN (SELECT id FROM material_category WHERE name='回装家具'))")
print(f"\n回装家具分类下物料数: {cur.fetchone()[0]}")

# 看看回装家具的L2子分类
cur.execute("SELECT id, name FROM material_category WHERE parent_id IN (SELECT id FROM material_category WHERE name='回装家具') ORDER BY sort_order")
print("\n回装家具L2分类:")
for r in cur.fetchall():
    print(r)
    # 每个L2下物料数
    cur2 = conn.cursor()
    cur2.execute("SELECT COUNT(*) FROM material_sku WHERE is_deleted=0 AND category_id=?", (r[0],))
    print(f"  -> {cur2.fetchone()[0]}条物料")

conn.close()
