import sqlite3
import os

db_path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\vanmoly_v3.db'
print(f"数据库: {db_path}")
print(f"文件存在: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='case_slide_config'")
if not cursor.fetchone():
    print("❌ case_slide_config 表不存在")
    conn.close()
    exit(1)

# 检查现有列
cursor.execute("PRAGMA table_info(case_slide_config)")
columns = [row[1] for row in cursor.fetchall()]
print(f"现有列: {columns}")

if 'about_subtitle' in columns:
    print("ℹ️ about_subtitle 列已存在，跳过")
else:
    cursor.execute("ALTER TABLE case_slide_config ADD COLUMN about_subtitle TEXT")
    conn.commit()
    print("✅ about_subtitle 列已添加")

# 验证
cursor.execute("PRAGMA table_info(case_slide_config)")
columns_after = [row[1] for row in cursor.fetchall()]
print(f"迁移后列: {columns_after}")

conn.close()
print("完成")
