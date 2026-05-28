import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cur = db.execute("PRAGMA table_info(case_space_materials)")
cols = [row[1] for row in cur.fetchall()]
required = ['custom_name','material','custom_measure','width','depth','height','category_level1','category_level2','color_name']
for f in required:
    print(f"  {f}: {'✅' if f in cols else '❌'}")
print(f"Total columns: {len(cols)}")
print("All cols:", cols)
db.close()
