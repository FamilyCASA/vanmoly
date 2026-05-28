import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# 1. Add width/depth/height to save_space_materials_full
old_save = """                custom_name=c.get('custom_name'),
                material=c.get('material'),
                custom_measure=c.get('custom_measure'),
                quantity=float(c.get('quantity', 1) or 1),"""

new_save = """                custom_name=c.get('custom_name'),
                material=c.get('material'),
                custom_measure=c.get('custom_measure'),
                width=float(c['width']) if c.get('width') else None,
                depth=float(c['depth']) if c.get('depth') else None,
                height=float(c['height']) if c.get('height') else None,
                quantity=float(c.get('quantity', 1) or 1),"""

c = c.replace(old_save, new_save, 1)
print("save_full: width/depth/height added")

# 2. Add width/depth/height to fallback dicts in get_slide_data
# Find all fallback SKU dict patterns
old_fallback = """                'supply_chain': sku.supply_chain or '',
                'color_name': sku.color_name or '',"""

new_fallback = """                'supply_chain': sku.supply_chain or '',
                'color_name': sku.color_name or '',
                'width': float(sku.width) if sku.width else None,
                'depth': float(sku.depth) if sku.depth else None,
                'height': float(sku.height) if sku.height else None,"""

count = c.count(old_fallback)
print(f"Found {count} fallback dict(s) to update")
c = c.replace(old_fallback, new_fallback)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("Done")
