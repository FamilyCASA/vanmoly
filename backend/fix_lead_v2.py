import re
path = r'D:\desktop\DESIGNARY-SYS-V3.0\backend\app\models\lead_v2.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
# Remove all __bind_key__ = 'lead' lines
content = re.sub(r"    __bind_key__ = 'lead'\n", '', content)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done. Removed all __bind_key__ = lead from lead_v2.py')
