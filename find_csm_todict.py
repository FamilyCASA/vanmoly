import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\backend\app\models\case.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Find CaseSpaceMaterial to_dict specifically
idx = content.find('class CaseSpaceMaterial')
if idx < 0:
    print("CaseSpaceMaterial NOT FOUND")
else:
    # Find to_dict after this class
    dict_idx = content.find('def to_dict', idx)
    # Find next class after to_dict
    next_class = content.find('\nclass ', dict_idx + 10)
    if next_class < 0: next_class = len(content)
    print("=== CaseSpaceMaterial.to_dict ===")
    print(content[dict_idx:next_class])
