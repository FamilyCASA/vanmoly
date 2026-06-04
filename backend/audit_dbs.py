import sqlite3, os

dbs = [
    ('auth.db',         r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\auth.db'),
    ('hr.db',           r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\hr.db'),
    ('lead.db',         r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\lead.db'),
    ('material.db',     r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\material.db'),
    ('vanmoly_v3.db',   r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'),
    ('case.db',         r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\case.db'),
    ('crm.db',          r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\crm.db'),
    ('finance.db',      r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\finance.db'),
    ('project.db',      r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\project.db'),
]
for name, path in dbs:
    size = os.path.getsize(path) if os.path.exists(path) else 0
    print(f'\n=== {name} ({size} bytes) ===')
    if size == 0:
        print('  [EMPTY]')
        continue
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    for (t,) in cur.fetchall():
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        cnt = cur.fetchone()[0]
        print(f'  {t}: {cnt} rows')
    conn.close()
