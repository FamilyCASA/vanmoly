import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
db.row_factory = sqlite3.Row

# Check case_space_materials - all fields
cur = db.execute("SELECT * FROM case_space_materials WHERE case_id=37")
rows = cur.fetchall()
print("=== case_space_materials ===")
for r in rows:
    d = dict(r)
    print(f"\nID {d['id']}:")
    for k, v in d.items():
        if v is not None:
            print(f"  {k}: {v}")

# Check material_sku table for these items
print("\n\n=== material_sku (matching) ===")
cur2 = db.execute("SELECT id, sku_code, material_name, category_level1, category_level2 FROM material_sku WHERE material_name LIKE '%备餐柜%' OR material_name LIKE '%柜门%' OR material_name LIKE '%柜体%' LIMIT 10")
for r in cur2.fetchall():
    print(f"  ID {r['id']}: sku={r['sku_code']}, name={r['material_name']}, cat1={r['category_level1']}, cat2={r['category_level2']}")

# Also check by sku_code if case_space_materials has it
print("\n=== material_sku (all with sku_code) ===")
cur3 = db.execute("SELECT id, sku_code, material_name FROM material_sku ORDER BY id DESC LIMIT 20")
for r in cur3.fetchall():
    print(f"  ID {r['id']}: sku={r['sku_code']}, name={r['material_name']}")

db.close()
