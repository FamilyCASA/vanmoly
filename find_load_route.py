import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'spaces.*materials' in line or '/materials' in line and 'GET' in lines[max(0,i-3):i+1]:
        print(f"Line {i}: {line.rstrip()}")
        for j in range(1, 6):
            if i+j < len(lines):
                print(f"Line {i+j}: {lines[i+j].rstrip()}")
        print("---")
