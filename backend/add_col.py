import sqlite3
conn = sqlite3.connect('D:/desktop/VANMOLY-SYS-V3.0/backend/instance/vanmoly_v3.db')
cur = conn.cursor()
cur.execute('PRAGMA table_info(case_study)')
cols = [r[1] for r in cur.fetchall()]
print('Current cols:', cols)
if 'is_virtual_customer' not in cols:
    cur.execute('ALTER TABLE case_study ADD COLUMN is_virtual_customer INTEGER DEFAULT 0')
    conn.commit()
    print('Column added')
else:
    print('Column exists')
conn.close()