# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app import db
from app.models import CaseStudy

# 查看案例表结构
print('=== 案例表结构 ===')
result = db.session.execute(db.text('PRAGMA table_info(case_study)'))
for row in result:
    print(f'{row[1]}: {row[2]}')

print()
print('=== 现有案例数据 ===')
result = db.session.execute(db.text('SELECT id, title, category, status FROM case_study LIMIT 10'))
for row in result:
    print(f'ID:{row[0]} | {row[1]} | 分类:{row[2]} | 状态:{row[3]}')