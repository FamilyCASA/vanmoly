import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Try different patterns
for pattern in ['sku.material_name', "'material_name': sku", '"material_name": sku', 'sku_name', 'MaterialSKU']:
    idx = c.find(pattern)
    if idx >= 0:
        print(f"Found '{pattern}' at offset {idx}")
        print(f"  Context: ...{c[max(0,idx-50):idx+100]}...")
    else:
        print(f"NOT found: '{pattern}'")
