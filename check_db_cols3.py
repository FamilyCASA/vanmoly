import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cur = db.execute("PRAGMA table_info(case_space_materials)")
cols = [(row[1], row[2]) for row in cur.fetchall()]
print("case_space_materials columns:")
for name, typ in cols:
    print(f"  {name}: {typ}")
db.close()
