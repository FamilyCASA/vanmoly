import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cur = conn.cursor()

# Check case 37 materials - all fields
cur.execute("""
SELECT id, sku_id, material_name, custom_name, custom_measure, 
       category_level1, category_level2, width, depth, height, unit
FROM case_space_materials 
WHERE case_id=37 
ORDER BY id
""")
rows = cur.fetchall()
print("=== 案例37 物料数据（前台显示相关）===")
print("id | sku_id | material_name | custom_name | custom_measure | cat1 | cat2 | w | d | h | unit")
for r in rows:
    print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} | {r[9]} | {r[10]}")

# Check if sku_ids have names
print("\n=== SKU名称验证 ===")
cur.execute("SELECT DISTINCT sku_id FROM case_space_materials WHERE case_id=37 AND sku_id IS NOT NULL")
sku_ids = [r[0] for r in cur.fetchall()]
for sid in sku_ids[:5]:
    cur.execute("SELECT id, name FROM material_sku WHERE id=?", (sid,))
    r = cur.fetchone()
    print(f"  sku_id={sid} -> {r[1] if r else 'NOT FOUND'}")

conn.close()
