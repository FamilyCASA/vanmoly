import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Get the full fallback dict block
idx = c.find("'material_name': sku.name")
if idx > 0:
    # Get surrounding 600 chars
    start = max(0, idx - 300)
    end = min(len(c), idx + 600)
    print(c[start:end])
