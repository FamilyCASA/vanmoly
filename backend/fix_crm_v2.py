import re
path = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\app\models\crm_v2.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = re.sub(r"    __bind_key__ = 'crm'\n", '', content)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
