import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find smat-table section
in_table = False
for i, line in enumerate(lines, 1):
    if 'smat-table' in line or 'smat-' in line:
        in_table = True
    if in_table:
        print(f"L{i}: {line.rstrip()}")
        if i > 3000 and '</table>' in line:
            break
