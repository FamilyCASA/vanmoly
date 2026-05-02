import sqlite3, json

conn = sqlite3.connect('D:/desktop/DESIGNARY-SYS-V3.0/backend/instance/vanmoly_v3.db')
conn.row_factory = sqlite3.Row

# 西映品牌产品
rows = conn.execute("SELECT id, name, brand, main_image, images FROM material_sku WHERE brand LIKE '%西映%' LIMIT 15").fetchall()
total = conn.execute("SELECT COUNT(*) FROM material_sku WHERE brand LIKE '%西映%'").fetchone()[0]
print(f'=== 西映品牌产品总数: {total} ===')
for r in rows:
    img = str(r['images'])[:80] if r['images'] else 'None'
    print(f'  ID:{r["id"]} | {r["name"]} | main:{r["main_image"] or "None"} | imgs:{img}')

print()
has_img = conn.execute("SELECT COUNT(*) FROM material_sku WHERE main_image IS NOT NULL AND main_image != ''").fetchone()[0]
no_img = conn.execute("SELECT COUNT(*) FROM material_sku WHERE (main_image IS NULL OR main_image = '')").fetchone()[0]
print(f'全库有主图: {has_img}, 无主图: {no_img}')

# 看看图片目录结构
import os
img_dir = 'D:/resources/vanmoly/materials/images'
for d in os.listdir(img_dir):
    full = os.path.join(img_dir, d)
    if os.path.isdir(full):
        files = [f for f in os.listdir(full) if f.lower().endswith(('.jpg','.png','.webp','.jpeg'))]
        print(f'  {d}/: {len(files)} files')
        if files:
            print(f'    示例: {files[0]}, {files[1] if len(files)>1 else ""}')

conn.close()
