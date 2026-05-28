import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find material table section
for i, line in enumerate(lines, 1):
    if 'smat-table' in line or 'material' in line.lower() and ('<th' in line or '<td' in line):
        print(f"Line {i}: {line.rstrip()}")
