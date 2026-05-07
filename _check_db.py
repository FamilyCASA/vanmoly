import sqlite3

conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
c = conn.cursor()

# Check space count
c.execute('SELECT COUNT(*) FROM case_space_renderings')
print(f'Spaces: {c.fetchone()[0]}')

# Check rendering count
c.execute('SELECT COUNT(*) FROM case_rendering_items')
print(f'Renderings: {c.fetchone()[0]}')

# Find ones with descriptions
c.execute('''
    SELECT r.id, r.space_id, r.title, r.description, s.space_name
    FROM case_rendering_items r
    JOIN case_space_renderings s ON r.space_id = s.id
    WHERE r.description IS NOT NULL AND r.description != ''
    ORDER BY r.id DESC
    LIMIT 10
''')
rows = c.fetchall()
print(f'Renderings with description: {len(rows)}')
for r in rows:
    print(f'  ID={r[0]}, space={r[4]}, title={r[2]}')
    desc = r[3] or ''
    print(f'  desc len={len(desc)}, preview={desc[:80]}')
    print()
conn.close()
