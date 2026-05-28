import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\components\case\phases\PhaseSpaceRenderingsEditor.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find el-table-column for material config
for i, line in enumerate(lines, 1):
    if 'el-table-column' in line and any(kw in line for kw in ['名称', '品牌', '规格', 'material_name', 'brand', 'spec', '花色', 'color_name']):
        print(f"{i}: {line.rstrip()[:150]}")
