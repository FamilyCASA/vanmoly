import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\routes\employee_routes.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找 update 或 create
for fn in ['update_employee', 'create_employee', 'update', 'create']:
    idx = content.find(f'def {fn}')
    if idx >= 0:
        end = content.find('\ndef ', idx+1) if '\ndef ' in content[idx+1:] else idx+1500
        print(f"=== {fn} ===")
        print(content[idx:end])
        print()
