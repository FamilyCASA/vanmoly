import re

with open(r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\admin\CaseEdit.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 找 script 部分关键方法
patterns = [
    r'const showcaseGrouped',
    r'const showcaseLoading',
    r'const loadShowcase',
    r'function loadShowcase',
    r'const selectedMaterial',
    r'showcase_material_ids',
    r'const saveSlideConfig',
    r'const slideConfig',
    r'const slideConfigLoaded',
    r'mounted.*\{',
    r'onMounted',
    r'watch\(.*slideConfig',
]

found = {}
for i, line in enumerate(content.splitlines(), 1):
    for p in patterns:
        if re.search(p, line, re.IGNORECASE):
            found[i] = line.rstrip()
            break

for i in sorted(found.keys()):
    print(f"{i:4d}: {found[i]}")
