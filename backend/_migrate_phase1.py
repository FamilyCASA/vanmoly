# -*- coding: utf-8 -*-
import sqlite3, os, shutil

DB = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'
BACKUP = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3_backup_workflow.db'

shutil.copy2(DB, BACKUP)
print('Backup:', BACKUP)

conn = sqlite3.connect(DB)
cur = conn.cursor()

for col_name, col_def in [
    ('is_real_case', 'INTEGER DEFAULT 0'),
    ('enable_public_workflow', 'INTEGER DEFAULT 0'),
    ('workflow_id', 'INTEGER'),
]:
    try:
        cur.execute(f'ALTER TABLE case_study ADD COLUMN {col_name} {col_def}')
        print('ADDED case_study.' + col_name)
    except Exception as e:
        print('case_study.' + col_name + ': ' + str(e))

try:
    cur.execute('ALTER TABLE customer_workflow ADD COLUMN case_id INTEGER')
    print('ADDED customer_workflow.case_id')
except Exception as e:
    print('customer_workflow.case_id: ' + str(e))

cur.execute('''CREATE TABLE IF NOT EXISTS case_workflow_timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    workflow_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    node_code VARCHAR(20),
    node_name VARCHAR(100),
    phase VARCHAR(50),
    phase_order INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    start_time DATETIME,
    end_time DATETIME,
    photos TEXT DEFAULT '[]',
    renderings TEXT DEFAULT '[]',
    notes TEXT,
    is_public INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
print('CREATED case_workflow_timeline')

cur.execute('''UPDATE case_study SET is_real_case=1
    WHERE customer_id IS NOT NULL
      AND building_id IS NOT NULL
      AND customer_id>0 AND building_id>0''')
print('Marked ' + str(cur.rowcount) + ' real cases')

conn.commit()
conn.close()
print('Done!')