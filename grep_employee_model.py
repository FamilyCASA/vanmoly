import sys, re
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\hr.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找 Employee class 定义
if 'class Employee' in content:
    idx = content.find('class Employee')
    end = content.find('\nclass ', idx+1) if '\nclass ' in content[idx+1:] else len(content)
    print("=== Employee Model ===")
    print(content[idx:idx+2000])
