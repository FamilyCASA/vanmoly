import sqlite3
conn = sqlite3.connect('instance/vanmoly_v3.db')
cur = conn.cursor()
cur.execute("SELECT id, name FROM material_category WHERE parent_id IS NULL ORDER BY sort_order")
for r in cur.fetchall():
    print(r)
print("---total L1---")

cur.execute("SELECT COUNT(*) FROM material_sku WHERE is_deleted=0 OR is_deleted IS NULL")
print("total materials:", cur.fetchone()[0])

cur.execute("SELECT name FROM material_sku WHERE is_deleted=0 LIMIT 10")
print("sample names:")
for r in cur.fetchall():
    print(" ", r)

conn.close()
