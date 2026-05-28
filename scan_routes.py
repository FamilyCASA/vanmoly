import sys; sys.stdout.reconfigure(encoding='utf-8')
import re

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\material_routes.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find all route definitions
routes = re.findall(r"@(\w+)\.route\(['\"]([^'\"]+)['\"].*?methods=\[([^\]]+)\].*?\n\s*def\s+(\w+)", content, re.DOTALL)
for bp, path_str, methods, fn_name in routes:
    print(f"{methods:15s} {path_str:50s} → {fn_name}")
