# -*- coding: utf-8 -*-
import sqlite3, json
db = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
row = db.execute("SELECT sections FROM page_config WHERE page_key='home' LIMIT 1").fetchone()
sections = json.loads(row[0])
for s in sections:
    comp = s.get('component', '')
    print(f"component={comp}, name={s.get('name','')}")
    if 'About' in comp or 'about' in comp:
        print(json.dumps(s, ensure_ascii=False, indent=2))

print("\n=== about page ===")
row2 = db.execute("SELECT sections FROM page_config WHERE page_key='about' LIMIT 1").fetchone()
if row2:
    sections2 = json.loads(row2[0])
    for s in sections2:
        comp = s.get('component', '')
        print(f"component={comp}, name={s.get('name','')}")
        if 'About' in comp or 'about' in comp or 'Brand' in comp:
            print(json.dumps(s, ensure_ascii=False, indent=2))
