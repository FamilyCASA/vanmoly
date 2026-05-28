import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Add material and custom fields to fallback dict
old_block = """                    'material_name': sku.name,
                    'material_image': sku.main_image,"""

new_block = """                    'material_name': sku.name,
                    'material_image': sku.main_image,
                    'material': sku.material or '',
                    'custom_name': '',
                    'custom_measure': '',"""

c = c.replace(old_block, new_block, 1)

# Check if there's a second occurrence (public_slide_data)
if old_block in c:
    c = c.replace(old_block, new_block, 1)
    print("✅ Updated second occurrence (public API)")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("✅ Fallback dict 添加 material/custom_name/custom_measure")
