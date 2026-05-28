import re

with open(r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\admin\CaseEdit.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 找 showcaseGrouped、showcaseLoading、loadShowcaseCandidates 等关键函数
patterns = [
    r'showcaseGrouped',
    r'showcaseLoading', 
    r'loadShowcaseCandidates',
    r'showcase_material_ids',
    r'showcase-candidates',
    r'saveSlideConfig',
    r'slideConfigLoaded',
    r'slideConfig[\.\s]',
]

found = set()
for i, line in enumerate(content.splitlines(), 1):
    for p in patterns:
        if re.search(p, line):
            found.add((i, line.rstrip()))
            break

for i, line in sorted(found):
    print(f"{i:4d}: {line}")
