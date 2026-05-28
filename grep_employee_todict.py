import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\hr.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找 to_dict
idx = content.find('def to_dict')
if idx >= 0:
    end = content.find('\n    def ', idx+1) if '\n    def ' in content[idx+1:] else idx+2000
    print(content[idx:end])
