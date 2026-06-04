import re
with open(r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\admin\CaseEdit.vue', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if any(kw in line for kw in ['视觉素材', '材质展示', 'slideConfig', '阶段', 'el-tab-pane']):
        print(f"{i}: {line.rstrip()}")
