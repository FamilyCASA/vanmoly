import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\case_routes.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find save_space_materials_full
idx = content.find('def save_space_materials_full')
if idx < 0:
    print("save_space_materials_full NOT FOUND")
else:
    end = content.find('\ndef ', idx+10)
    print("=== save_space_materials_full ===")
    print(content[idx:end])
