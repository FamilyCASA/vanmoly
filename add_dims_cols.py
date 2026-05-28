import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
for col in ['width', 'depth', 'height']:
    try:
        conn.execute(f'ALTER TABLE case_space_materials ADD COLUMN {col} NUMERIC(10,2)')
        print(f'OK Added {col}')
    except Exception as e:
        if 'duplicate column' in str(e).lower():
            print(f'SKIP {col} already exists')
        else:
            print(f'ERR {col}: {e}')
conn.commit()
conn.close()
