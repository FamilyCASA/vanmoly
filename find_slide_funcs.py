import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'def get_slide_data' in line or 'def get_public_slide_data' in line:
        print(f"Line {i}: {line.rstrip()}")
