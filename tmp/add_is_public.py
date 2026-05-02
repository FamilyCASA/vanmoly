# -*- coding: utf-8 -*-
"""
Add is_public column to material_sku table
"""
import sqlite3
import shutil
from datetime import datetime
import os

# Paths
db_path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'
backup_path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.db'

# Backup
if os.path.exists(db_path):
    shutil.copy2(db_path, backup_path)
    print(f'Backup: {backup_path}')

# Connect
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(material_sku)")
columns = [col[1] for col in cursor.fetchall()]

if 'is_public' not in columns:
    cursor.execute("ALTER TABLE material_sku ADD COLUMN is_public BOOLEAN DEFAULT 1")
    conn.commit()
    print('Added is_public column to material_sku')
else:
    print('is_public column already exists')

# Verify
cursor.execute("PRAGMA table_info(material_sku)")
columns = [col[1] for col in cursor.fetchall()]
print(f'Columns: {columns}')

conn.close()
print('Done')
