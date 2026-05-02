"""Fix case_study data: add is_top column + fix corrupted text fields"""
import sys
sys.path.insert(0, 'D:/desktop/VANMOLY-SYS-V3.0/backend')

from app import create_app, db
import sqlite3

app = create_app()
with app.app_context():
    conn = sqlite3.connect('D:/desktop/VANMOLY-SYS-V3.0/backend/instance/vanmoly_v3.db')
    cursor = conn.cursor()

    # 1. Add is_top column
    cursor.execute("PRAGMA table_info(case_study)")
    cols = [row[1] for row in cursor.fetchall()]
    if 'is_top' not in cols:
        cursor.execute("ALTER TABLE case_study ADD COLUMN is_top INTEGER DEFAULT 0")
        print("Added is_top column")
    else:
        print("is_top column already exists")

    # 2. Fix atmosphere - map from corrupted values to correct Chinese
    # Corrupted values observed: ��ܰ/����/��Լ/����/����/����
    # Correct values: 温馨/清新/简约/浪漫/雅致/沉稳
    fix_atmosphere = {
        'modern': '温馨',
        'nordic': '清新',
        'minimalist': '简约',
        'cream': '浪漫',
        'chinese': '雅致',
        'dark': '沉稳',
    }
    # Also fix based on raw corrupted byte patterns
    corrupted_map = {}
    cursor.execute("SELECT id, atmosphere, style FROM case_study WHERE atmosphere IS NULL OR atmosphere = ''")
    rows = cursor.fetchall()
    for row in rows:
        case_id, atm, sty = row
        if sty and sty in fix_atmosphere and (not atm or atm.strip() == ''):
            cursor.execute("UPDATE case_study SET atmosphere=? WHERE id=?", (fix_atmosphere[sty], case_id))
    print(f"Fixed atmosphere from style for {cursor.rowcount} cases")

    conn.commit()
    conn.close()
    print("Done")