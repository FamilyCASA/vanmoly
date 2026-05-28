import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'spaceMaterialsMap' in line or 'getSpaceMaterial' in line or 'matPage' in line:
        print(f"Line {i}: {line.rstrip()}")
