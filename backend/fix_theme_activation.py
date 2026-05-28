# -*- coding: utf-8 -*-
"""Fix theme activation: activate plan_a_warm_dark (暗黑), deactivate others"""
import sqlite3

conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
c = conn.cursor()

# Deactivate all themes
c.execute('UPDATE theme_config SET is_active=0')

# Activate plan_a_warm_dark (暗黑 template - Plan A we're currently using)
c.execute("UPDATE theme_config SET is_active=1 WHERE theme_key='plan_a_warm_dark'")

conn.commit()
print('Theme activation updated:')
c.execute('SELECT id, theme_key, theme_name, is_active FROM theme_config ORDER BY id')
for row in c.fetchall():
    print(f'  id={row[0]}, key={row[1]}, active={row[3]}')
conn.close()
print('\nDone! plan_a_warm_dark is now active (暗黑 · 暖光奢华)')
