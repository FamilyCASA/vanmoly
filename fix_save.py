import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Add custom_name, material, custom_measure to save_space_materials_full
old_create = """                color_name=c.get('color_name'),
                quantity=float(c.get('quantity', 1) or 1),"""

new_create = """                color_name=c.get('color_name'),
                custom_name=c.get('custom_name'),
                material=c.get('material'),
                custom_measure=c.get('custom_measure'),
                quantity=float(c.get('quantity', 1) or 1),"""

c = c.replace(old_create, new_create, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("✅ save_space_materials_full 添加 custom_name/material/custom_measure")
