path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find get_public_slide_data
for i, line in enumerate(lines):
    if 'def get_public_slide_data' in line:
        for j in range(i, min(i+60, len(lines))):
            print(f"  {j+1}: {lines[j].rstrip()}")
        break
