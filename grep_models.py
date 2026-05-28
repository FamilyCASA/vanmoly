path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all class definitions and relationship definitions
import re
classes = re.findall(r'class (\w+).*?models\.Model\)', content)
print("Models in case.py:", classes)

# Find all db.Table and relationship definitions
for m in re.finditer(r'(?:db\.Table\(|class \w+.*?Model\)).*?(?=\nclass |\n# =====|\Z)', content, re.DOTALL):
    block = m.group()[:300]
    if 'team' in block.lower() or 'member' in block.lower():
        print("FOUND:", block[:200])
