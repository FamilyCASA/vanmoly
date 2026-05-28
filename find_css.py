import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find material table CSS
in_css = False
for i, line in enumerate(lines, 1):
    if '物料配置表' in line or 'smat-table' in line or 'space-material' in line:
        in_css = True
    if in_css:
        print(f"{i}: {line.rstrip()}")
        if line.strip() == '}' and in_css and i > 2100:
            in_css = False
            print()
