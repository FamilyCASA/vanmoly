# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 为案例添加多图轮播和瀑布流功能
1. 添加 hero_images 列到 case_study 表
2. 添加 gallery 列到 case_study 表
3. 将已上传到 upload/images 的文件关联到 case_media 表
"""
import os
import sys
import sqlite3
import shutil
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r'D:\desktop\VANMOLY-SYS-V3.0\backend\instance\vanmoly_v3.db'
UPLOAD_DIR = r'D:\desktop\VANMOLY-SYS-V3.0\backend\upload\images\2026\05'

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. 添加 hero_images 列
    print('1. 添加 hero_images 列...')
    try:
        cur.execute("ALTER TABLE case_study ADD COLUMN hero_images TEXT")
        print('  hero_images 列已添加')
    except Exception as e:
        print(f'  hero_images 列已存在或添加失败: {e}')

    # 2. 添加 gallery 列
    print('2. 添加 gallery 列...')
    try:
        cur.execute("ALTER TABLE case_study ADD COLUMN gallery TEXT")
        print('  gallery 列已添加')
    except Exception as e:
        print(f'  gallery 列已存在或添加失败: {e}')

    # 3. 扫描上传目录，找出属于案例36的文件
    print('3. 扫描上传文件...')
    if not os.path.exists(UPLOAD_DIR):
        print(f'  上传目录不存在: {UPLOAD_DIR}')
        return

    # 获取所有属于案例36的图片文件（根据时间戳推断：21:57:28 ~ 21:57:57 期间上传）
    # 这些是用户上传的30张效果图
    all_files = []
    for f in os.listdir(UPLOAD_DIR):
        fpath = os.path.join(UPLOAD_DIR, f)
        if os.path.isfile(fpath):
            all_files.append((f, fpath))

    print(f'  找到 {len(all_files)} 个文件')

    # 4. 列出目前 case_media 中已有的记录
    cur.execute('SELECT id, case_id, url FROM case_media ORDER BY id DESC LIMIT 10')
    existing_media = cur.fetchall()
    print(f'  case_media 已有 {len(existing_media)} 条记录')

    # 5. 列出目前 case_study 的 hero_images 列数据
    cur.execute('SELECT id, hero_images FROM case_study WHERE id=36')
    row = cur.fetchone()
    print(f'  案例36 hero_images 字段: {row[1] if row else "无"}')

    # 6. 关联上传文件到 case_media 表
    print('6. 关联文件到 case_media 表...')
    # 收集需要处理的案例36的文件（16-33序号范围）
    case36_files = []
    for f, fpath in all_files:
        # 文件格式: 20260501_215728_16_xxx.jpg 或 20260501_215757_16_xxx.jpg
        try:
            parts = f.split('_')
            if len(parts) >= 3:
                seq = int(parts[2])
                if 16 <= seq <= 33:
                    case36_files.append((f, fpath, seq))
        except:
            pass

    print(f'  案例36相关文件: {len(case36_files)} 个')

    # 按序号排序
    case36_files.sort(key=lambda x: x[2])

    # 写入 case_media 表
    for f, fpath, seq in case36_files:
        url_path = f'/upload/images/2026/05/{f}'
        # 检查是否已存在
        cur.execute('SELECT id FROM case_media WHERE case_id=36 AND url=?', (url_path,))
        if cur.fetchone():
            print(f'  文件已关联: {f}')
            continue

        cur.execute('''
            INSERT INTO case_media (case_id, media_type, url, sort_order, created_at)
            VALUES (36, 'image', ?, ?, datetime('now', '+8 hours'))
        ''', (url_path, seq))
        print(f'  插入: {f} (序号{seq})')

    conn.commit()

    # 7. 设置案例36的 hero_images（取前5张作为轮播图）
    print('7. 设置案例36的 hero_images...')
    hero_urls = []
    for f, fpath, seq in case36_files[:5]:
        hero_urls.append(f'/upload/images/2026/05/{f}')

    if hero_urls:
        import json
        hero_json = json.dumps(hero_urls, ensure_ascii=False)
        cur.execute('UPDATE case_study SET hero_images=? WHERE id=36', (hero_json,))
        conn.commit()
        print(f'  hero_images 已设置: {hero_urls}')

    # 8. 设置案例36的 gallery（其余25张作为瀑布流图集）
    print('8. 设置案例36的 gallery...')
    gallery_urls = []
    for f, fpath, seq in case36_files[5:]:
        gallery_urls.append(f'/upload/images/2026/05/{f}')

    if gallery_urls:
        import json
        gallery_json = json.dumps(gallery_urls, ensure_ascii=False)
        cur.execute('UPDATE case_study SET gallery=? WHERE id=36', (gallery_json,))
        conn.commit()
        print(f'  gallery 已设置: {len(gallery_urls)} 张')

    # 9. 统计结果
    print('\n=== 迁移完成 ===')
    cur.execute('SELECT COUNT(*) FROM case_media WHERE case_id=36')
    count = cur.fetchone()[0]
    print(f'案例36的 case_media 记录数: {count}')

    cur.execute('SELECT hero_images, gallery FROM case_study WHERE id=36')
    row = cur.fetchone()
    print(f'hero_images: {row[0][:100] if row[0] else "无"}...')
    print(f'gallery: {row[1][:100] if row[1] else "无"}...')

    conn.close()
    print('\n迁移成功！请重启后端服务。')

if __name__ == '__main__':
    run_migration()
