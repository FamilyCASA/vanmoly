import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
db.row_factory = sqlite3.Row
cur = db.execute("SELECT id, custom_name, material_name, custom_measure, width, depth, height, quantity FROM case_space_materials WHERE case_id=37")
rows = cur.fetchall()
print(f"Total rows: {len(rows)}")
for r in rows:
    print(f"\nID {r['id']}:")
    print(f"  custom_name: {r['custom_name']!r}")
    print(f"  material_name: {r['material_name']!r}")
    print(f"  custom_measure: {r['custom_measure']!r}")
    print(f"  width: {r['width']}, depth: {r['depth']}, height: {r['height']}")
    print(f"  quantity: {r['quantity']}")
    # Calculate what custom_measure should be
    w, d, h = r['width'] or 0, r['depth'] or 0, r['height'] or 0
    if w and d and h:
        calc = (w * d * h) / 1000000000  # convert to cubic meters
        print(f"  Calculated measure: {calc:.4f} m³")
db.close()
