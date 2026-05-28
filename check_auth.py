import sys; sys.stdout.reconfigure(encoding='utf-8')
import re

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\material_routes.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find jwt_required_v2 import or definition
for kw in ['jwt_required_v2', 'from app', 'import jwt']:
    idx = content.find(kw)
    if idx > 0:
        line_start = content.rfind('\n', 0, idx) + 1
        line_end = content.find('\n', idx)
        print(content[line_start:line_end].strip())

# Check batch_import route header
idx = content.find('def batch_import_materials')
if idx > 0:
    start = content.rfind('@', 0, idx)
    end = content.find('"""', idx)
    print("\n--- batch_import route ---")
    print(content[start:end+10])
