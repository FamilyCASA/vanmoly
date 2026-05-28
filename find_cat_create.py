import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\material_routes.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find create_category function
idx = content.find('def create_category')
if idx > 0:
    next_fn = content.find('\n@material_bp.route', idx + 10)
    if next_fn == -1:
        next_fn = idx + 2000
    print(content[idx:next_fn])
