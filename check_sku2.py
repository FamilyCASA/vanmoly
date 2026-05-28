import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')

# Check material_sku table schema
cur = db.execute("PRAGMA table_info(material_sku)")
cols = [r[1] for r in cur.fetchall()]
print(f"material_sku columns: {cols}")

# Get SKU 293 and 660
cur = db.execute(f"SELECT * FROM material_sku WHERE id IN (293, 660)")
for r in cur.fetchall():
    d = dict(zip(cols, r))
    print(f"\nSKU ID {d.get('id')}:")
    for k, v in d.items():
        if v is not None:
            print(f"  {k}: {v}")
db.close()
