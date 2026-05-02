"""
更新西映物料的主图
由于图片是按顺序提取的，我们按物料导入顺序分配图片
"""
import sqlite3
import json
import os
from pathlib import Path

DB_PATH = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\instance\vanmoly_v3.db'
IMAGE_BASE_URL = '/static/uploads/xiying'
IMAGE_DIR = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\static\uploads\xiying'

def get_image_files(prefix):
    """获取指定前缀的图片文件列表，按数字排序"""
    files = []
    for f in os.listdir(IMAGE_DIR):
        if f.startswith(prefix + '_image') and f.endswith(('.jpeg', '.jpg', '.png')):
            # 提取数字
            try:
                num = int(f.replace(prefix + '_image', '').split('.')[0])
                files.append((num, f))
            except:
                continue
    return [f[1] for f in sorted(files)]

def update_material_images():
    """更新物料主图"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有西映物料，按ID排序（导入顺序）
    cursor.execute("""
        SELECT id, sku_code, name, category_id 
        FROM material_sku 
        WHERE sku_code LIKE 'XY-%' 
        ORDER BY id
    """)
    materials = cursor.fetchall()
    
    # 按分类分组
    chair_materials = [m for m in materials if m[1].startswith('XY-CY-')]
    table_materials = [m for m in materials if m[1].startswith('XY-CZ-')]
    furniture_materials = [m for m in materials if not m[1].startswith('XY-CY-') and not m[1].startswith('XY-CZ-')]
    
    print(f"餐椅物料: {len(chair_materials)} 条")
    print(f"餐桌物料: {len(table_materials)} 条")
    print(f"家居配套物料: {len(furniture_materials)} 条")
    
    # 获取各分类图片
    chair_images = get_image_files('chair')
    table_images = get_image_files('table')
    furniture_images = get_image_files('furniture')
    
    print(f"\n餐椅图片: {len(chair_images)} 张")
    print(f"餐桌图片: {len(table_images)} 张")
    print(f"家居配套图片: {len(furniture_images)} 张")
    
    updated_count = 0
    
    # 更新餐椅图片
    for i, material in enumerate(chair_materials):
        if i < len(chair_images):
            image_url = f"{IMAGE_BASE_URL}/{chair_images[i]}"
            cursor.execute("""
                UPDATE material_sku 
                SET main_image = ? 
                WHERE id = ?
            """, (image_url, material[0]))
            updated_count += 1
            print(f"更新餐椅: {material[1]} -> {chair_images[i]}")
    
    # 更新餐桌图片
    for i, material in enumerate(table_materials):
        if i < len(table_images):
            image_url = f"{IMAGE_BASE_URL}/{table_images[i]}"
            cursor.execute("""
                UPDATE material_sku 
                SET main_image = ? 
                WHERE id = ?
            """, (image_url, material[0]))
            updated_count += 1
            print(f"更新餐桌: {material[1]} -> {table_images[i]}")
    
    # 更新家居配套图片
    for i, material in enumerate(furniture_materials):
        if i < len(furniture_images):
            image_url = f"{IMAGE_BASE_URL}/{furniture_images[i]}"
            cursor.execute("""
                UPDATE material_sku 
                SET main_image = ? 
                WHERE id = ?
            """, (image_url, material[0]))
            updated_count += 1
            print(f"更新家居配套: {material[1]} -> {furniture_images[i]}")
    
    conn.commit()
    conn.close()
    
    return updated_count

def main():
    print("=" * 60)
    print("西映物料主图更新")
    print("=" * 60)
    
    updated = update_material_images()
    
    print("\n" + "=" * 60)
    print(f"更新完成! 共更新 {updated} 条物料的主图")
    print("=" * 60)

if __name__ == '__main__':
    main()
