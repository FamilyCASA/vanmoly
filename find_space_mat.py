import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'space' in line.lower() and 'material' in line.lower():
        print(f"Line {i}: {line.rstrip()}")
