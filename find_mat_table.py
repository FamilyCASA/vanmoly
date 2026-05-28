import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find material table sections
for i, line in enumerate(lines, 1):
    if any(kw in line for kw in ['物料配置', 'material-table', 'space-material', 'cat-material', 'material_name', 'category_level', '花色', 'color_name', '规格', 'spec']):
        print(f"{i}: {line.rstrip()[:150]}")
