import sqlite3

db_path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\auth.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# List tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print('Tables:', tables)

# Check employee 42
if 'employee' in tables:
    cur.execute('SELECT id, name, department_id, position_id, email FROM employee WHERE id = 42')
    row = cur.fetchone()
    print('Employee 42:', row)
    cur.execute('PRAGMA table_info(employee)')
    cols = [c[1] for c in cur.fetchall()]
    print('All cols:', cols)
elif 'hr_employee_v2' in tables:
    cur.execute('SELECT id, name, department_id FROM hr_employee_v2 WHERE id = 42')
    row = cur.fetchone()
    print('HR Employee 42:', row)
    cur.execute('PRAGMA table_info(hr_employee_v2)')
    cols = [c[1] for c in cur.fetchall()]
    print('All cols:', cols)

conn.close()
