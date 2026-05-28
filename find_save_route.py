import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find save_space_materials_full
for i, line in enumerate(lines, 1):
    if 'save_space_materials_full' in line or 'spaces.*full' in line or '/full' in line:
        print(f"Line {i}: {line.rstrip()}")
