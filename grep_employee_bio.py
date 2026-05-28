import sys, re
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\hr.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找 title 字段后面的内容
idx = content.find("title = db.Column")
if idx >= 0:
    print(content[idx:idx+800])
