import sys; sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Find material config table template
for i, line in enumerate(lines, 1):
    if any(kw in line for kw in ['material-config', 'mc-table', 'mc-heading', 'space_mat_', 'cat_mat_', 'materialDetailItem']):
        print(f'{i}: {line.rstrip()[:130]}')
