import sqlite3
conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cur = conn.execute('PRAGMA table_info(case_space_materials)')
cols = [r[1] for r in cur.fetchall()]
print('All columns:', cols)
for c in ['custom_name', 'material', 'custom_measure']:
    print(f'  {c}: {"EXISTS" if c in cols else "MISSING"}')
