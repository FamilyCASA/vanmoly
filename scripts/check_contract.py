import sqlite3

DB_PATH = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print('contract表结构:')
cursor.execute("PRAGMA table_info(contract)")
for col in cursor.fetchall():
    print(f'  {col[1]} ({col[2]})')

print('\nquote表结构:')
cursor.execute("PRAGMA table_info(quote)")
for col in cursor.fetchall():
    print(f'  {col[1]} ({col[2]})')

conn.close()
