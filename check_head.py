import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\material_routes.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find first 20 lines
for i, line in enumerate(content.split('\n')[:20], 1):
    print(f"{i:3d}: {line}")
