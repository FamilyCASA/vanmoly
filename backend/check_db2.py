import sqlite3
conn = sqlite3.connect('instance/vanmoly_v3.db')
cur = conn.cursor()
# 搜索澜缦集
cur.execute("SELECT id, name FROM material_sku WHERE name LIKE '%澜缦集%'")
rows = cur.fetchall()
print(f"keyword match: {len(rows)}")
for r in rows[:5]:
    print(r)

# 回装家具L2分类
cur.execute("SELECT id, name FROM material_category WHERE parent_id=25 ORDER BY sort_order")
print("\n回装家具 L2:")
for r in cur.fetchall():
    cur2 = conn.cursor()
    cur2.execute("SELECT COUNT(*) FROM material_sku WHERE (is_deleted=0 OR is_deleted IS NULL) AND category_id=?", (r[0],))
    cnt = cur2.fetchone()[0]
    print(f"  {r[0]} {r[1]} -> {cnt} items")

# 柜门分类下物料
cur.execute("SELECT id, name FROM material_category WHERE name='柜门' AND parent_id=25")
rows = cur.fetchall()
print(f"\n柜门 category: {rows}")
if rows:
    cid = rows[0][0]
    cur.execute("SELECT COUNT(*) FROM material_sku WHERE (is_deleted=0 OR is_deleted IS NULL) AND category_id=?", (cid,))
    print(f"柜门下物料数: {cur.fetchone()[0]}")

conn.close()
