import sqlite3

db_path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print('All tables:', tables)
conn.close()
