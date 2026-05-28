import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3, json
db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
db.row_factory = sqlite3.Row
cur = db.execute("SELECT * FROM case_space_materials WHERE case_id=37 ORDER BY id")
rows = cur.fetchall()
print(f"Total: {len(rows)}")
for r in rows:
    d = dict(r)
    print(f"\n--- id={d['id']} material_name={d['material_name']} ---")
    for k in ['custom_name','category_level1','category_level2','material','color_name','custom_measure','width','depth','height','brand','spec','unit_price','quantity']:
        v = d.get(k)
        print(f"  {k}: {v!r}")
db.close()
