# -*- coding: utf-8 -*-
path = r'D:\desktop\VANMOLY-SYS-V3.0\frontend\src\views\cases\CaseSlidePreview.vue'
with open(path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'teamMembers' in line or 'team_members' in line or 'pageAbout' in line or 'page_about' in line:
            print(f"  {i}: {line.rstrip()}")
