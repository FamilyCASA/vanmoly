import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查 case_study 表是否有 scene_tag 列
cursor.execute("PRAGMA table_info(case_study)")
cols = [r[1] for r in cursor.fetchall()]
print("当前列:", cols)

if 'scene_tag' not in cols:
    cursor.execute("ALTER TABLE case_study ADD COLUMN scene_tag VARCHAR(50)")
    conn.commit()
    print("[OK] scene_tag 列已添加")
else:
    print("[OK] scene_tag 列已存在")

conn.close()
print("[DONE]")
