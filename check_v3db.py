import sqlite3

db_path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# List tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print('Tables:', tables[:20])

# Check employee 42
for tbl in ['employee', 'hr_employee_v2']:
    if tbl in tables:
        cur.execute(f'SELECT id, name, department_id, position_id, email FROM {tbl} WHERE id = 42')
        row = cur.fetchone()
        print(f'{tbl} 42:', row)

conn.close()
