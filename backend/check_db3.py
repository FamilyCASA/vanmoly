import sqlite3
conn = sqlite3.connect('instance/vanmoly_v3.db')
cur = conn.cursor()
# 模糊搜索澜缦集
cur.execute("SELECT id, name, brand, category_id FROM material_sku WHERE name LIKE '%澜%' OR brand LIKE '%澜%' LIMIT 10")
rows = cur.fetchall()
print(f"'澜' match: {len(rows)}")
for r in rows:
    print(r)

# 也搜缦
cur.execute("SELECT id, name, brand FROM material_sku WHERE name LIKE '%缦%' OR brand LIKE '%缦%' LIMIT 10")
rows = cur.fetchall()
print(f"\n'缦' match: {len(rows)}")
for r in rows:
    print(r)

# 搜集
cur.execute("SELECT id, name, brand FROM material_sku WHERE name LIKE '%集%' OR brand LIKE '%集%' LIMIT 10")
rows = cur.fetchall()
print(f"\n'集' match: {len(rows)}")
for r in rows:
    print(r)

conn.close()
