import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# 1. Check save_space_materials_full for width/depth/height
idx = c.find('def save_space_materials_full')
if idx > 0:
    block = c[idx:idx+2000]
    for field in ['width', 'depth', 'height']:
        print(f'save_full.{field}: {"YES" if field in block else "NO"}')

# 2. Check fallback dict in get_slide_data / get_public_slide_data
for func_name in ['def get_slide_data', 'def get_public_slide_data']:
    idx2 = c.find(func_name)
    if idx2 > 0:
        block2 = c[idx2:idx2+5000]
        for field in ['width', 'depth', 'height']:
            print(f'{func_name}.{field}: {"YES" if field in block2 else "NO"}')
