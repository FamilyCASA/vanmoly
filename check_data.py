import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
db.row_factory = sqlite3.Row
cur = db.execute("SELECT * FROM case_space_materials WHERE case_id=37")
rows = cur.fetchall()
print(f"Total rows: {len(rows)}")
for r in rows:
    print(f"\n  id={r['id']}, space_name={r['space_name']}")
    print(f"  material_name={r['material_name']}")
    print(f"  custom_name={r['custom_name']!r}, custom_measure={r['custom_measure']!r}")
    print(f"  category_level1={r['category_level1']!r}, category_level2={r['category_level2']!r}")
    print(f"  width={r['width']}, depth={r['depth']}, height={r['height']}")
    print(f"  material={r['material']!r}, spec={r['spec']!r}")
db.close()
