# -*- coding: utf-8 -*-
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'slidePages' in line and ('=' in line):
        for j in range(i, min(i+30, len(lines))):
            print(f"  {j+1}: {lines[j].rstrip()}")
        print()
        break
