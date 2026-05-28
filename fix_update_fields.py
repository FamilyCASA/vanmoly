import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Add missing fields to update_space_material whitelist
old_fields = """'brand', 'spec', 'unit', 'env_level', 'supply_chain', 'color_name',
                       'quantity', 'unit_price', 'total_price', 'sort_order']"""

new_fields = """'brand', 'spec', 'unit', 'env_level', 'supply_chain', 'color_name',
                       'custom_name', 'material', 'custom_measure', 'width', 'depth', 'height',
                       'quantity', 'unit_price', 'total_price', 'sort_order']"""

c = c.replace(old_fields, new_fields, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("OK: update_space_material whitelist updated with custom_name/material/custom_measure/width/depth/height")
