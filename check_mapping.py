import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
db.row_factory = sqlite3.Row

# Check if to_dict includes sku original name
cur = db.execute("SELECT sku_id, material_name FROM case_space_materials WHERE case_id=37")
for r in cur.fetchall():
    sku_id = r['sku_id']
    mat_name = r['material_name']
    
    # Get original SKU name
    cur2 = db.execute("SELECT name, material FROM material_sku WHERE id=?", (sku_id,))
    sku = cur2.fetchone()
    orig = sku['name'] if sku else 'N/A'
    print(f"sku_id={sku_id} | material_name(自定义)={mat_name} | sku.name(原始)={orig}")

db.close()
