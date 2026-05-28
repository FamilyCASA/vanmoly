import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find the fallback dict construction from MaterialSKU
# Look for 'material_name': sku
idx = c.find("'material_name': sku.material_name")
while idx > 0:
    line_start = c.rfind('\n', 0, idx) + 1
    line_end = c.find('\n', idx)
    line = c[line_start:line_end]
    print(f"Found at {idx}: {line.strip()[:120]}")
    
    # Check if 'material' field is already in nearby context
    nearby = c[max(0,idx-200):idx+400]
    if "'material':" in nearby or "'material': " in nearby:
        print("  ✅ material field already exists nearby")
    else:
        # Add material field after material_name
        old = "'material_name': sku.material_name,"
        new = "'material_name': sku.material_name,\n                    'material': sku.material or '',"
        # Find exact position
        exact = c.find(old, idx - 50)
        if exact > 0:
            c = c[:exact] + new + c[exact + len(old):]
            print("  ✅ Added material field")
    
    idx = c.find("'material_name': sku.material_name", idx + 30)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
