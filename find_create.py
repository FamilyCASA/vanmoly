import sys; sys.stdout.reconfigure(encoding='utf-8')
import re

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\material_routes.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find create_material function
idx = content.find('def create_material')
if idx > 0:
    # Find the next function definition
    next_fn = content.find('\ndef ', idx + 10)
    print(content[idx:next_fn if next_fn > 0 else idx + 2000])
