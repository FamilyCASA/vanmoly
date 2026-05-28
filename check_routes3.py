import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Check fallback dict for width/depth/height
for field in ['width', 'depth', 'height']:
    count = c.count(f"'{field}':")
    print(f"  '{field}': appears {count} times in routes")

# Check save_space_materials_full
save_idx = c.find('def save_space_materials_full')
if save_idx > 0:
    block = c[save_idx:save_idx+2000]
    for field in ['width', 'depth', 'height', 'custom_name', 'material', 'custom_measure']:
        print(f"  save.{field}: {'✅' if field in block else '❌'}")

# Check update_space_material whitelist
update_idx = c.find('def update_space_material')
if update_idx > 0:
    block2 = c[update_idx:update_idx+1000]
    for field in ['width', 'depth', 'height', 'custom_name', 'material', 'custom_measure']:
        print(f"  update.{field}: {'✅' if field in block2 else '❌'}")
