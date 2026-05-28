import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

# Search for sku.material_name patterns
import re
matches = list(re.finditer(r"sku\.material_name", c))
for m in matches:
    start = max(0, m.start() - 100)
    end = min(len(c), m.end() + 300)
    ctx = c[start:end]
    print(f"--- Context around offset {m.start()} ---")
    print(ctx[:400])
    print()
