import sys; sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cur = db.execute("PRAGMA table_info(case_media)")
cols = [row[1] for row in cur.fetchall()]
print("Current case_media columns:", cols)

# Check which columns are missing from the model
model_cols = ['id', 'case_id', 'media_type', 'url', 'thumbnail', 'custom_name', 'material', 'custom_measure', 'sort_order', 'description', 'created_at']
missing = [c for c in model_cols if c not in cols]
print(f"Missing columns: {missing}")

# Add missing columns
for col in missing:
    try:
        db.execute(f"ALTER TABLE case_media ADD COLUMN {col} TEXT")
        print(f"  Added: {col}")
    except Exception as e:
        print(f"  Error adding {col}: {e}")

db.commit()
db.close()
print("Done")
