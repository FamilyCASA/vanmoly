"""Check case_study table schema and values"""
import sys
sys.path.insert(0, 'D:/desktop/VANMOLY-SYS-V3.0/backend')

from app import create_app, db
import sqlite3

app = create_app()
with app.app_context():
    conn = sqlite3.connect('D:/desktop/VANMOLY-SYS-V3.0/backend/instance/vanmoly_v3.db')
    cursor = conn.cursor()
    
    # Table columns
    cursor.execute("PRAGMA table_info(case_study)")
    cols = [row[1] for row in cursor.fetchall()]
    print('=== case_study columns ===')
    for c in cols:
        print(f'  {c}')
    
    # Atmosphere values
    cursor.execute("SELECT DISTINCT atmosphere FROM case_study WHERE atmosphere IS NOT NULL AND atmosphere != ''")
    atms = [row[0] for row in cursor.fetchall()]
    print('\n=== atmosphere values ===')
    print(atms)
    
    # space_type values
    cursor.execute("SELECT DISTINCT space_type FROM case_study WHERE space_type IS NOT NULL AND space_type != ''")
    sts = [row[0] for row in cursor.fetchall()]
    print('\n=== space_type values ===')
    print(sts)
    
    # house_type values
    cursor.execute("SELECT DISTINCT house_type FROM case_study WHERE house_type IS NOT NULL AND house_type != ''")
    hts = [row[0] for row in cursor.fetchall()]
    print('\n=== house_type values ===')
    print(hts)
    
    # style values
    cursor.execute("SELECT DISTINCT style FROM case_study WHERE style IS NOT NULL AND style != ''")
    styles = [row[0] for row in cursor.fetchall()]
    print('\n=== style values ===')
    print(styles)
    
    # Check is_top
    print('\n=== is_top exists? ===')
    print('is_top' in cols)
    
    conn.close()