import sys
sys.stdout.reconfigure(encoding='utf-8')

import shutil
import os
from pathlib import Path

# 目录配置
SOURCE_DIR = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\static\uploads\xiying'
TARGET_BASE = r'D:\resources\vanmoly\materials'

# 创建目录结构
dirs = {
    'chairs': f'{TARGET_BASE}/images/chairs',
    'tables': f'{TARGET_BASE}/images/tables', 
    'furniture': f'{TARGET_BASE}/images/furniture',
    'videos': f'{TARGET_BASE}/videos',
    'thumbs': f'{TARGET_BASE}/images/thumbnails',
}

print("=" * 60)
print("整理物料资源文件")
print("=" * 60)

for name, path in dirs.items():
    os.makedirs(path, exist_ok=True)
    print(f"✓ 创建目录: {path}")

# 按分类复制图片
print("\n【复制图片文件】")

copied = {'chairs': 0, 'tables': 0, 'furniture': 0}

for filename in os.listdir(SOURCE_DIR):
    source_path = os.path.join(SOURCE_DIR, filename)
    
    if filename.startswith('chair_'):
        target = os.path.join(dirs['chairs'], filename)
        shutil.copy2(source_path, target)
        copied['chairs'] += 1
    elif filename.startswith('table_'):
        target = os.path.join(dirs['tables'], filename)
        shutil.copy2(source_path, target)
        copied['tables'] += 1
    elif filename.startswith('furniture_'):
        target = os.path.join(dirs['furniture'], filename)
        shutil.copy2(source_path, target)
        copied['furniture'] += 1

print(f"  餐椅图片: {copied['chairs']} 张 → {dirs['chairs']}")
print(f"  餐桌图片: {copied['tables']} 张 → {dirs['tables']}")
print(f"  家居配套: {copied['furniture']} 张 → {dirs['furniture']}")

# 创建符号链接（软链接）让后端可以访问
print("\n【创建符号链接】")
link_dir = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\static\uploads\materials'
os.makedirs(link_dir, exist_ok=True)

try:
    # Windows需要管理员权限创建符号链接，这里改用junction或复制
    # 创建一个小脚本来设置正确的路径映射
    mapping_file = os.path.join(link_dir, 'README.txt')
    with open(mapping_file, 'w', encoding='utf-8') as f:
        f.write("""物料资源目录映射
========================

实际资源位置: D:\resources\vanmoly\materials\

目录结构:
  images/
    chairs/      - 餐椅图片
    tables/      - 餐桌图片
    furniture/   - 家居配套图片
    thumbnails/  - 缩略图
  videos/        - 产品视频

使用说明:
  生产环境建议配置Nginx/Apache直接服务静态资源
  开发环境可通过软链接或修改后端配置指向实际目录
""")
    print(f"✓ 创建映射说明: {mapping_file}")
except Exception as e:
    print(f"✗ 创建映射失败: {e}")

# 生成配置文件
print("\n【生成资源配置】")
config_content = """# 物料资源目录配置
# 将此配置添加到后端 config.py

MATERIAL_ASSETS = {
    'base_path': r'D:\\resources\\vanmoly\\materials',
    'images': {
        'chairs': r'D:\\resources\\vanmoly\\materials\\images\\chairs',
        'tables': r'D:\\resources\\vanmoly\\materials\\images\\tables',
        'furniture': r'D:\\resources\\vanmoly\\materials\\images\\furniture',
        'thumbnails': r'D:\\resources\\vanmoly\\materials\\images\\thumbnails',
    },
    'videos': r'D:\\resources\\vanmoly\\materials\\videos',
    'url_prefix': '/materials',
}

# 静态文件服务配置（生产环境Nginx示例）
# location /materials/images/ {
#     alias D:/resources/vanmoly/materials/images/;
#     expires 30d;
# }
# location /materials/videos/ {
#     alias D:/resources/vanmoly/materials/videos/;
#     expires 30d;
# }
"""

config_file = r'D:\desktop\DESIGNARY-SYS-V3.0\MATERIAL_ASSETS_CONFIG.py'
with open(config_file, 'w', encoding='utf-8') as f:
    f.write(config_content)
print(f"✓ 配置文件: {config_file}")

print("\n" + "=" * 60)
print("资源整理完成！")
print("=" * 60)
print(f"\n总图片数: {sum(copied.values())} 张")
print(f"资源根目录: {TARGET_BASE}")
print("\n建议:")
print("  1. 生产环境配置Nginx直接服务静态资源")
print("  2. 大视频文件建议存放到对象存储(OSS/S3)")
print("  3. 图片建议生成多尺寸缩略图优化加载")
