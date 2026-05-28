# -*- coding: utf-8 -*-
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find slideIndex function
for i, line in enumerate(lines):
    if 'slideIndex' in line and ('function' in line or 'const slideIndex' in line or '= (' in line):
        for j in range(i, min(i+20, len(lines))):
            print(f"  {j+1}: {lines[j].rstrip()}")
        print()
