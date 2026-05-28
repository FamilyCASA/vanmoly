import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find CaseSpaceMaterial to_dict
idx = content.find('class CaseSpaceMaterial')
if idx >= 0:
    print("=== CaseSpaceMaterial class ===")
    print(content[idx:idx+2000])
