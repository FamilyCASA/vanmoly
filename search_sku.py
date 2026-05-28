import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Find where SKU dict is built in get_slide_data / get_public_slide_data
# Search for 'sku.material_name'
idx = 0
while True:
    idx = c.find('sku.material_name', idx)
    if idx < 0:
        break
    start = max(0, idx - 200)
    end = min(len(c), idx + 500)
    ctx = c[start:end]
    print(f"=== Found sku.material_name at offset {idx} ===")
    print(ctx[:400])
    print()
    idx += 20
