# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\desktop\VANMOLY-SYS-V3.0\backend')

from app import create_app
app = create_app()
ctx = app.test_request_context()
ctx.push()

from app.models.case import CaseStudy, CaseMedia
import json

c = CaseStudy.query.get(36)
print('=== 案例36 字段检查 ===')
print(f'hero_images: {c.hero_images}')
print(f'gallery: {c.gallery}')
print(f'cover_image: {c.cover_image}')
print(f'is_top: {getattr(c, "is_top", "NOT_IN_MODEL")}')

# 检查 case_media
media = CaseMedia.query.filter_by(case_id=36).all()
print(f'\ncase_media 记录数: {len(media)}')
for m in media[:5]:
    print(f'  id={m.id} url={m.url} sort={m.sort_order}')
if len(media) > 5:
    print(f'  ... 还有 {len(media)-5} 条')

# 检查数据库列
import sqlite3
conn = sqlite3.connect(r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info(case_study)")
cols = [row[1] for row in cur.fetchall()]
print(f'\ncase_study 表列: {cols}')
has_is_top = 'is_top' in cols
has_top_position = 'top_position' in cols
print(f'is_top 列存在: {has_is_top}')
print(f'top_position 列存在: {has_top_position}')
conn.close()
