import sqlite3
DB_PATH = r'D:\desktop\VANMOLY-SYS-V3.0\backend\vanmoly_v3.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
rows = cursor.fetchall()
for r in rows:
    print(r[0])
conn.close()
