"""
为 case_slide_configs 表添加新的幻灯片配置列
- aspect_ratio: 画幅比例 (16:9, 21:9, 4:3)
- inner_bg_image: 内页背景图URL
- back_bg_image: 封底背景图URL
"""
import sqlite3
import sys

DB_PATH = r'D:\desktop\VANMOLY-SYS-V3.0\backend\vanmoly_v3.db'

def get_table_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}

def add_column(cursor, table, col_name, col_def):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
        print(f"  [OK] Added: {col_name}")
        return True
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
            print(f"  [SKIP] Already exists: {col_name}")
            return False
        else:
            print(f"  [FAIL] {col_name}: {e}")
            return False

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    table = 'case_slide_configs'
    cols = get_table_columns(cursor, table)
    print(f"\nCurrent columns in '{table}':")
    for c in sorted(cols):
        print(f"  - {c}")

    new_cols = {
        'aspect_ratio': "TEXT DEFAULT '16:9'",
        'inner_bg_image': 'TEXT',
        'back_bg_image': 'TEXT',
    }

    print(f"\nAdding new columns:")
    for col_name, col_def in new_cols.items():
        add_column(cursor, table, col_name, col_def)

    conn.commit()

    # Verify
    cols_after = get_table_columns(cursor, table)
    print(f"\nColumns after migration:")
    for c in sorted(cols_after):
        print(f"  - {c}")

    conn.close()
    print("\n[Done] Database migration complete.")

if __name__ == '__main__':
    main()
