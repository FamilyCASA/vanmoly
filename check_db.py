import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cur = conn.cursor()

# Check case 37 materials - sku_id and material_name
cur.execute("SELECT id, sku_id, sku_code, material_name, custom_name, custom_measure FROM case_space_materials WHERE case_id=37 LIMIT 10")
rows = cur.fetchall()
print("=== 案例37 物料数据 ===")
for r in rows:
    print(r)

# Check if sku_ids match material_sku table
print("\n=== sku_id 分布 ===")
cur.execute("SELECT COUNT(*), CASE WHEN sku_id IS NULL THEN 'NULL' WHEN sku_id='' THEN 'EMPTY' ELSE 'HAS_VALUE' END FROM case_space_materials WHERE case_id=37")
print(cur.fetchone())

# Check a specific sku_id
cur.execute("SELECT DISTINCT sku_id FROM case_space_materials WHERE case_id=37 AND sku_id IS NOT NULL AND sku_id != '' LIMIT 5")
sku_ids = [r[0] for r in cur.fetchall()]
print(f"\n=== 验证 sku_id 在 material_sku 表中是否存在 ===")
for sid in sku_ids:
    cur.execute("SELECT id, name FROM material_sku WHERE id=?", (sid,))
    r = cur.fetchone()
    print(f"  sku_id={sid} -> {r}")

conn.close()
