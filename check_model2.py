import sys; sys.stdout.reconfigure(encoding='utf-8')

# 1. Check CaseSpaceMaterial model fields
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, encoding='utf-8') as f:
    c = f.read()

idx = c.find('class CaseSpaceMaterial')
end = c.find('\nclass ', idx + 10)
if end < 0: end = len(c)
block = c[idx:end]

# Check for width/depth/height fields
for field in ['width', 'depth', 'height', 'custom_name', 'custom_measure', 'material', 'category_level1', 'category_level2']:
    found = f'self.{field}' in block or f'db.Column(db' in block and f"'{field}'" in block or f'{field} = db.Column' in block
    print(f'CaseSpaceMaterial.{field}: {"✅" if found else "❌"}')

# 2. Check to_dict output
idx2 = c.find('def to_dict(self):', idx)
if idx2 > 0:
    dict_block = c[idx2:end]
    for field in ['width', 'depth', 'height', 'custom_name', 'custom_measure', 'material', 'category_level1', 'category_level2']:
        found = f"'{field}'" in dict_block or f'self.{field}' in dict_block
        print(f'  to_dict.{field}: {"✅" if found else "❌"}')
