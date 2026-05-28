# -*- coding: utf-8 -*-
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Print lines around the team section (line 90-125)
for i in range(89, min(125, len(lines))):
    print(f"  {i+1}: {lines[i].rstrip()}")
